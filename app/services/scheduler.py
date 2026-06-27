# сторонние
import json
import logging
import asyncio
from datetime import datetime
from zoneinfo import ZoneInfo

# types
from aiogram import Bot

# DB
from AI_SMM_AGENT.app.services.database import get_db

# services
from AI_SMM_AGENT.app.services.post_service import publish_to_channel

# settings
from AI_SMM_AGENT.app.config.settings import settings


logger = logging.getLogger(__name__)


async def run_scheduler(bot: Bot) -> None:
    while True:
        await asyncio.sleep(60)
        await check_and_publish(bot)

async def check_and_publish(bot: Bot) -> None:
    db = await get_db()
    now = datetime.now(ZoneInfo("Europe/Moscow")).strftime("%Y-%m-%d %H:%M:%S")
    cursor = await db.execute(
        "SELECT * FROM posts WHERE status = 'scheduled' AND scheduled_at <= ?", (now,)
    )
    rows = await cursor.fetchall()
    for row in rows:
        try:
            post_data = json.loads(row["draft_json"])
            text = post_data.get("text", "")
            selected_media_ids = post_data.get("selected_media_ids", [])

            draft_object = {
                "media": [{"file_id": fid, "type": "photo"} for fid in selected_media_ids],
                "selected_media_ids": selected_media_ids
            }

            await publish_to_channel(
                bot=bot,
                channel_id=settings.CHANNEL_ID,
                text=text,
                draft_object=draft_object
            )

            await db.execute(
                "UPDATE posts SET status = 'published', published_at = ? WHERE post_id = ?",
                (datetime.now(ZoneInfo("Europe/Moscow")).strftime("%Y-%m-%d %H:%M:%S"), row["post_id"])
            )
            await db.commit()
            logger.info("Пост был успешно опубликован в канал") # Добавить маркеры для поста по типу ID, времени, общей темы (пост про, ИИ в СРМ системах 2026 года, ID: 123, время публикации 12:00)

        except Exception as e:
            logger.error(f"Ошибка публикации scheduled поста {row['post_id']}: {e}", exc_info=True)