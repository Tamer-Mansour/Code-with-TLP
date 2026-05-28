from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field


class UserSettingsRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)
    id: int
    user_id: int
    theme: str
    font_family: str
    color_scheme: str
    background_image_url: str | None = None
    profile_layout: str
    created_at: datetime
    updated_at: datetime


class UserSettingsUpdate(BaseModel):
    theme: str | None = Field(default=None, pattern=r"^(light|dark)$")
    font_family: str | None = Field(default=None, pattern=r"^(Inter|Roboto|Outfit|JetBrains Mono|Fira Code|Poppins|Nunito|Open Sans|Lato|Montserrat|Raleway|Ubuntu|Source Sans 3|DM Sans|Space Grotesk|Tajawal|Cairo|Amiri|Noto Naskh Arabic|El Messiri|Changa|Readex Pro)$")
    color_scheme: str | None = Field(default=None, pattern=r"^(blue|green|purple|amber|rose|cyan|slate|red|orange|yellow|lime|emerald|teal|sky|indigo|violet|pink)$")
    background_image_url: str | None = None
    profile_layout: str | None = Field(default=None, pattern=r"^(default|minimal|split)$")
