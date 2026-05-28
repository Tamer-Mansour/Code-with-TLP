from typing import TYPE_CHECKING
from sqlalchemy import ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.models.base import Base, TimestampMixin

if TYPE_CHECKING:
    from app.models.user import User


class UserSettings(Base, TimestampMixin):
    __tablename__ = "user_settings"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(
        ForeignKey("users.id", ondelete="CASCADE"),
        unique=True,
        nullable=False,
    )

    theme: Mapped[str] = mapped_column(String(32), default="dark", nullable=False)
    font_family: Mapped[str] = mapped_column(String(64), default="Inter", nullable=False)
    color_scheme: Mapped[str] = mapped_column(String(64), default="blue", nullable=False)
    background_image_url: Mapped[str | None] = mapped_column(String(512))
    profile_layout: Mapped[str] = mapped_column(String(64), default="default", nullable=False)

    user: Mapped["User"] = relationship(back_populates="settings")
