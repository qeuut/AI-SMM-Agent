from pydantic import BaseModel
from datetime import datetime


class ReturnedPostStat(BaseModel):
    quantity_posts: int
    quantity_scheduled: int
    quantity_published: int
    last_post_status: str

    last_post_date: datetime | None = None
    last_post_about: str | None = None
    last_scheduled_post_date: datetime | None = None
    last_published_post_date: datetime | None = None