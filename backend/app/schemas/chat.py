from __future__ import annotations

from pydantic import BaseModel, ConfigDict


# ── Provider catalogue ──────────────────────────────────────────────────────

class ProviderInfo(BaseModel):
    id: str
    name: str
    base_url: str
    models: list[str]
    openai_compatible: bool


# ── API-key management ──────────────────────────────────────────────────────

class AIKeyCreate(BaseModel):
    provider: str
    api_key: str
    base_url: str | None = None
    default_model: str | None = None
    label: str | None = None


class AIKeyRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    provider: str
    base_url: str | None = None
    default_model: str | None = None
    label: str | None = None
    masked_key: str  # computed — never the raw value


# ── Chat sessions ───────────────────────────────────────────────────────────

class ChatSessionCreate(BaseModel):
    title: str = "New Chat"


class ChatSessionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    provider: str | None = None
    model: str | None = None


# ── Chat messages ───────────────────────────────────────────────────────────

class ChatMessageRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    role: str
    content: str
    model: str | None = None


class ChatSessionDetail(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    title: str
    provider: str | None = None
    model: str | None = None
    messages: list[ChatMessageRead] = []


# ── Sending a message ───────────────────────────────────────────────────────

class ChatAttachment(BaseModel):
    name: str
    content: str  # extracted text content of the attached file


class ChatSend(BaseModel):
    message: str
    provider: str | None = None
    model: str | None = None
    attachments: list[ChatAttachment] = []


class ChatSendResponse(BaseModel):
    reply: str
    model: str
