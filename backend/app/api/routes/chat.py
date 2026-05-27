"""TLP Chat routes — bring-your-own-key multi-provider chat (Phase 0, no RAG).

Prefix : /ai
Tags   : ai
Auth   : all endpoints require a valid Bearer token (get_current_user)
"""

from __future__ import annotations

import json

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.core.crypto import decrypt, encrypt
from app.core.database import SessionLocal, get_db
from app.models.ai import ChatMessage, ChatSession, UserAIKey
from app.models.user import User
from app.schemas.chat import (
    AIKeyCreate,
    AIKeyRead,
    ChatAttachment,
    ChatMessageRead,
    ChatSend,
    ChatSendResponse,
    ChatSessionCreate,
    ChatSessionDetail,
    ChatSessionRead,
    ProviderInfo,
)
from app.services.llm_gateway import (
    PROVIDERS,
    chat_complete,
    chat_complete_stream,
    get_provider,
)

router = APIRouter(prefix="/ai", tags=["ai"])

_SYSTEM_PROMPT = (
    "You are TLP Chat, a helpful CS tutor for the Code with TLP learning platform."
)


def _augment(message: str, attachments: list[ChatAttachment]) -> str:
    """Fold attached file text into the user message sent to the model."""
    if not attachments:
        return message
    parts: list[str] = [message] if message else []
    for a in attachments:
        clipped = a.content[:20000]  # guard against oversized files
        parts.append(f"\n[Attached file: {a.name}]\n```\n{clipped}\n```")
    return "\n".join(parts).strip()


def _resolve_key(db: Session, current: User, provider_id: str | None) -> UserAIKey:
    user_key: UserAIKey | None = None
    if provider_id:
        user_key = db.scalar(
            select(UserAIKey).where(
                UserAIKey.user_id == current.id,
                UserAIKey.provider == provider_id,
            )
        )
    if user_key is None:
        user_key = db.scalar(select(UserAIKey).where(UserAIKey.user_id == current.id))
    if user_key is None:
        raise HTTPException(status_code=400, detail="No API key configured. Add one in Settings.")
    return user_key


# ── Helper ──────────────────────────────────────────────────────────────────

def _masked(encrypted_key: str) -> str:
    """Return a masked representation — never expose the raw key."""
    try:
        raw = decrypt(encrypted_key)
        suffix = raw[-4:] if len(raw) >= 4 else raw
    except Exception:
        suffix = "????"
    return f"sk-…{suffix}"


# ── Providers ───────────────────────────────────────────────────────────────

@router.get("/providers", response_model=list[ProviderInfo])
def list_providers(
    _: User = Depends(get_current_user),
):
    """Return the catalogue of supported LLM providers."""
    return PROVIDERS


# ── API-key management ───────────────────────────────────────────────────────

@router.get("/keys", response_model=list[AIKeyRead])
def list_keys(
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    """List the current user's stored provider keys (masked)."""
    rows = list(
        db.scalars(
            select(UserAIKey).where(UserAIKey.user_id == current.id)
        ).all()
    )
    return [
        AIKeyRead(
            id=row.id,
            provider=row.provider,
            base_url=row.base_url,
            default_model=row.default_model,
            label=row.label,
            masked_key=_masked(row.encrypted_key),
        )
        for row in rows
    ]


@router.post("/keys", response_model=AIKeyRead, status_code=201)
def add_key(
    payload: AIKeyCreate,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    """Store a new provider API key (encrypted at rest)."""
    key = UserAIKey(
        user_id=current.id,
        provider=payload.provider,
        encrypted_key=encrypt(payload.api_key),
        base_url=payload.base_url,
        default_model=payload.default_model,
        label=payload.label,
    )
    db.add(key)
    db.commit()
    db.refresh(key)
    return AIKeyRead(
        id=key.id,
        provider=key.provider,
        base_url=key.base_url,
        default_model=key.default_model,
        label=key.label,
        masked_key=_masked(key.encrypted_key),
    )


@router.delete("/keys/{key_id}", status_code=204)
def delete_key(
    key_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    """Delete one of the current user's provider keys."""
    key = db.scalar(
        select(UserAIKey).where(
            UserAIKey.id == key_id,
            UserAIKey.user_id == current.id,
        )
    )
    if key is None:
        raise HTTPException(status_code=404, detail="API key not found.")
    db.delete(key)
    db.commit()


# ── Chat sessions ────────────────────────────────────────────────────────────

@router.get("/chat/sessions", response_model=list[ChatSessionRead])
def list_sessions(
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    """List all chat sessions for the current user."""
    return list(
        db.scalars(
            select(ChatSession)
            .where(ChatSession.user_id == current.id)
            .order_by(ChatSession.id.desc())
        ).all()
    )


@router.post("/chat/sessions", response_model=ChatSessionRead, status_code=201)
def create_session(
    payload: ChatSessionCreate = ChatSessionCreate(),
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    """Create a new chat session."""
    session = ChatSession(user_id=current.id, title=payload.title)
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


@router.get("/chat/sessions/{session_id}", response_model=ChatSessionDetail)
def get_session(
    session_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    """Return a session together with its full message history."""
    session = db.scalar(
        select(ChatSession).where(
            ChatSession.id == session_id,
            ChatSession.user_id == current.id,
        )
    )
    if session is None:
        raise HTTPException(status_code=404, detail="Chat session not found.")
    return session


@router.delete("/chat/sessions/{session_id}", status_code=204)
def delete_session(
    session_id: int,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    """Delete a chat session and all its messages (cascade)."""
    session = db.scalar(
        select(ChatSession).where(
            ChatSession.id == session_id,
            ChatSession.user_id == current.id,
        )
    )
    if session is None:
        raise HTTPException(status_code=404, detail="Chat session not found.")
    db.delete(session)
    db.commit()


# ── Sending a message ────────────────────────────────────────────────────────

@router.post("/chat/sessions/{session_id}/messages", response_model=ChatSendResponse)
def send_message(
    session_id: int,
    payload: ChatSend,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    """Append a user message, call the LLM, persist and return the reply."""
    # Validate session ownership.
    session = db.scalar(
        select(ChatSession).where(
            ChatSession.id == session_id,
            ChatSession.user_id == current.id,
        )
    )
    if session is None:
        raise HTTPException(status_code=404, detail="Chat session not found.")

    # Resolve provider & model — payload overrides session defaults.
    provider_id = payload.provider or session.provider
    model = payload.model or session.model

    # Find the best matching API key for the chosen provider.
    user_key: UserAIKey | None = None
    if provider_id:
        user_key = db.scalar(
            select(UserAIKey).where(
                UserAIKey.user_id == current.id,
                UserAIKey.provider == provider_id,
            )
        )
    if user_key is None:
        # Fall back to the user's first stored key.
        user_key = db.scalar(
            select(UserAIKey).where(UserAIKey.user_id == current.id)
        )
    if user_key is None:
        raise HTTPException(
            status_code=400,
            detail="No API key configured. Add one in Settings.",
        )

    # Resolve final provider / model from the key if still unset.
    if provider_id is None:
        provider_id = user_key.provider
    provider_info = get_provider(provider_id)
    if provider_info is None:
        raise HTTPException(status_code=400, detail=f"Unknown provider '{provider_id}'.")

    if model is None:
        model = user_key.default_model or provider_info.models[0]

    base_url = user_key.base_url or provider_info.base_url

    augmented = _augment(payload.message, payload.attachments)

    # Persist the user's message.
    user_msg = ChatMessage(
        session_id=session_id,
        role="user",
        content=augmented,
    )
    db.add(user_msg)
    db.flush()  # assign id without committing yet

    # Build the message list for the API call.
    prior = list(
        db.scalars(
            select(ChatMessage)
            .where(
                ChatMessage.session_id == session_id,
                ChatMessage.id != user_msg.id,
            )
            .order_by(ChatMessage.id)
        ).all()
    )
    messages = [{"role": "system", "content": _SYSTEM_PROMPT}]
    messages += [{"role": m.role, "content": m.content} for m in prior]
    messages.append({"role": "user", "content": augmented})

    # Call the LLM (may raise HTTPException 502).
    raw_key = decrypt(user_key.encrypted_key)
    reply_text = chat_complete(
        provider=provider_id,
        api_key=raw_key,
        base_url=base_url,
        model=model,
        messages=messages,
    )

    # Persist the assistant reply.
    assistant_msg = ChatMessage(
        session_id=session_id,
        role="assistant",
        content=reply_text,
        model=model,
    )
    db.add(assistant_msg)

    # Update session metadata if this is the first time provider/model are set.
    if session.provider is None:
        session.provider = provider_id
    if session.model is None:
        session.model = model

    db.commit()
    return ChatSendResponse(reply=reply_text, model=model)


# ── Streaming a message (SSE) ─────────────────────────────────────────────────

@router.post("/chat/sessions/{session_id}/messages/stream")
def stream_message(
    session_id: int,
    payload: ChatSend,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    """Same as send_message but streams the reply token-by-token over SSE.

    Events are JSON lines: {"token": "..."} repeatedly, then {"done": true, "model": "..."}.
    On failure a {"error": "..."} event is emitted.
    """
    session = db.scalar(
        select(ChatSession).where(
            ChatSession.id == session_id,
            ChatSession.user_id == current.id,
        )
    )
    if session is None:
        raise HTTPException(status_code=404, detail="Chat session not found.")

    provider_id = payload.provider or session.provider
    model = payload.model or session.model
    user_key = _resolve_key(db, current, provider_id)

    if provider_id is None:
        provider_id = user_key.provider
    provider_info = get_provider(provider_id)
    if provider_info is None:
        raise HTTPException(status_code=400, detail=f"Unknown provider '{provider_id}'.")
    if model is None:
        model = user_key.default_model or provider_info.models[0]
    base_url = user_key.base_url or provider_info.base_url

    augmented = _augment(payload.message, payload.attachments)
    user_msg = ChatMessage(session_id=session_id, role="user", content=augmented)
    db.add(user_msg)
    db.flush()

    prior = list(
        db.scalars(
            select(ChatMessage)
            .where(ChatMessage.session_id == session_id, ChatMessage.id != user_msg.id)
            .order_by(ChatMessage.id)
        ).all()
    )
    messages = [{"role": "system", "content": _SYSTEM_PROMPT}]
    messages += [{"role": m.role, "content": m.content} for m in prior]
    messages.append({"role": "user", "content": augmented})

    raw_key = decrypt(user_key.encrypted_key)
    if session.provider is None:
        session.provider = provider_id
    if session.model is None:
        session.model = model
    # Persist the user message + session metadata before streaming begins.
    db.commit()

    # Capture plain values for the generator (request-scoped db will be closed).
    sid, mdl, pid, burl = session_id, model, provider_id, base_url

    def event_stream():
        collected: list[str] = []
        try:
            for token in chat_complete_stream(pid, raw_key, burl, mdl, messages):
                collected.append(token)
                yield f"data: {json.dumps({'token': token})}\n\n"
        except HTTPException as exc:
            yield f"data: {json.dumps({'error': exc.detail})}\n\n"
        text = "".join(collected)
        if text:
            with SessionLocal() as s2:
                s2.add(ChatMessage(session_id=sid, role="assistant", content=text, model=mdl))
                s2.commit()
        yield f"data: {json.dumps({'done': True, 'model': mdl})}\n\n"

    return StreamingResponse(
        event_stream(),
        media_type="text/event-stream",
        headers={"Cache-Control": "no-cache", "X-Accel-Buffering": "no"},
    )
