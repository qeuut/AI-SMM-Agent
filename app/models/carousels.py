from dataclasses import dataclass, field
from typing import Any


@dataclass
class CarouselPostData:
    post_id: int
    user_id: int
    status: str
    date: str
    text: str
    published_msg_ids: str
    selected_media_ids: list[int] = field(default_factory=list)


@dataclass
class CarouselResponse:
    total_count: int
    current_page: int
    post: CarouselPostData

    @staticmethod
    def parse_row_to_post(row: Any) -> CarouselPostData:
        display_date = (
                row["scheduled_at"]
                or row["published_at"]
                or row["created_at"]
        )

        draft_dict = row["draft_json"]

        if isinstance(draft_dict, dict):
            post_text = draft_dict.get("text", "Текст поста отсутствует")
            selected_media_ids = draft_dict.get("selected_media_ids", [])
        else:
            selected_media_ids = []
            post_text = "Черновик пуст"

        msg_ids = row["channel_message_ids"]
        published_msg_ids = str(msg_ids) if msg_ids else ""

        return CarouselPostData(
            post_id=int(row["post_id"]),
            user_id=int(row["user_id"]),
            status=str(row["status"]),
            date=str(display_date),
            text=str(post_text),
            published_msg_ids=published_msg_ids,
            selected_media_ids=selected_media_ids
        )