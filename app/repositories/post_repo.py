import uuid
import json
import logging

from AI_SMM_AGENT.app.services.database import get_db
from AI_SMM_AGENT.app.models.sessions_modes import SessionModes
from AI_SMM_AGENT.app.models.stat_of_post import ReturnedPostStat

logger = logging.getLogger(__name__)


async def db_created_post(user_id: int, draft_json: str, time: str | None, status: str, at: str = "") -> int:
    if at not in ["created_at", "scheduled_at", "published_at"]:
        logger.error("Аргумент ---at--- в функции ---db_created_post--- не равен ожидаемому значению. Взято значение: created_at")
        at = "created_at"

    db = await get_db()

    cursor = await db.execute(f"""
            INSERT INTO posts (user_id, draft_json, {at}, status) values(?, ?, ?, ?)""",
            (user_id, draft_json, time, status))

    await db.commit()
    return cursor.lastrowid


async def get_all_posts(user_id: int) -> ReturnedPostStat | None:
    db = await get_db()
    cursor = await db.execute(
        "SELECT * FROM posts WHERE user_id = ?", (user_id,)
    )

    rows = await cursor.fetchall()

    if not rows:
        return None

    # счетчики и переменные для дат за один проход цикла
    quantity_scheduled = 0
    quantity_published = 0
    last_scheduled_post_date = None
    last_published_post_date = None

    for row in rows:
        if row["scheduled_at"]:
            quantity_scheduled += 1
            last_scheduled_post_date = row["scheduled_at"]

        if row["published_at"]:
            quantity_published += 1
            last_published_post_date = row["published_at"]

    # последняя строка
    last_row = rows[-1]

    # текст поста из джсон
    try:
        post_data = json.loads(last_row["draft_json"])
        post_text = post_data.get("text", "Медиа-файл без текста")
    except (json.JSONDecodeError, TypeError):
        post_text = "Не удалось прочитать текст"

    last_post_about = (post_text[:60] + "..." if len(post_text) > 60 else post_text)

    if last_row["scheduled_at"]:
        last_post_status = "Запланирован"
        last_post_date = last_row["scheduled_at"]
    elif last_row["published_at"]:
        last_post_status = "Опубликован"
        last_post_date = last_row["published_at"]
    else:
        last_post_status = "Сгенерирован"
        last_post_date = last_row[
            "created_at"
        ]

    return ReturnedPostStat(
        quantity_posts=len(rows),
        quantity_scheduled=quantity_scheduled,
        quantity_published=quantity_published,
        last_post_status=last_post_status,
        last_post_date=last_post_date,
        last_post_about=last_post_about,
        last_scheduled_post_date=last_scheduled_post_date,
        last_published_post_date=last_published_post_date,
    )
