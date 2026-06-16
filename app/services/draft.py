import logging

from AI_SMM_AGENT.app.models.data_models import DraftPost, MediaItem
from AI_SMM_AGENT.app.models.draft import MediaInput, MediaType

logger = logging.getLogger(__name__)


def draft_working(media_items: list[MediaInput], object_of_draft: DraftPost) -> tuple[int, int, DraftPost]:
    sum_photos = 0
    sum_videos = 0

    for item in media_items:
        if item.type == "text":
            object_of_draft.text_parts.append(item.text)

        elif item.type in (MediaType.PHOTO, MediaType.VIDEO, MediaType.VOICE):
            object_of_draft.media.append(MediaItem(
                type=item.type,
                file_id=item.file_id,
                caption=item.caption
            ))
            sum_photos += (item.type == MediaType.PHOTO)
            sum_videos += (item.type == MediaType.VIDEO)

        else:
            logger.warning(f"Неизвестный тип данных: {item.type}")

    return sum_photos, sum_videos, object_of_draft