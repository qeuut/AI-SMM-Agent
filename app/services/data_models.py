from AI_SMM_AGENT.app.models.draft import MediaType
from pydantic import BaseModel, ConfigDict


class MediaItem(BaseModel):
    type: MediaType # тоже, самое что и literal["photo", video...]
    file_id: str | None = None
    caption: str | None = None


class DraftPost(BaseModel):
    model_config = ConfigDict(validate_assignment=True) # отслеживание малых изменений структур данных по типу append и др.

    media: list[MediaItem] = []
    text_parts: list[str] = []
    selected_media_ids: list[str] = []