from AI_SMM_AGENT.app.models.data_models import DraftPost


def get_photos_from_draft(draft: DraftPost, draft_dict: dict) -> list[dict]:
    """Возвращает список фото в порядке selected_media_ids."""
    media_index = {m["file_id"]: m for m in draft_dict.get("media", [])}
    return [
        media_index[fid] for fid in draft.selected_media_ids
        if fid in media_index and media_index[fid]["type"] == "photo"
    ]
