from pydantic import BaseModel
from typing import Literal
from enum import Enum


class MediaType(str, Enum):
    PHOTO: str = "photo"
    VIDEO: str = "video"
    VOICE: str = "voice"
    TEXT: str = "text"


class MediaInput(BaseModel):
    type: MediaType
    file_id: str | None = None
    caption: str | None = None
    text: str | None = None
    url: str | None = None