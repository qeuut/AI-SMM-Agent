import aiosqlite
import logging

from AI_SMM_AGENT.app.repositories.database import get_db

logger = logging.getLogger(__name__)


async def change_media_ids(user_id: int, selected_media_ids: list[str]) -> bool:
    db = await get_db()
    media_ids_str = ",".join(selected_media_ids) # 123,456,789

    try:
        await db.execute("UPDATE posts SET selected_media_ids = ? WHERE user_id = ?", (media_ids_str, user_id))
        await db.commit()
        logger.info("selected_media_ids успешно записано в БД")

    except aiosqlite.Error as e:
        logger.critical(f"Ошибка при записи selected_media_ids({media_ids_str}) в БД: {e}")
        return False
    return True


async def get_media_from_db(user_id: int) -> list | None:
    db = await get_db()
    cursor = await db.execute("SELECT selected_media_ids FROM posts WHERE user_id = ?", (user_id,))
    row = await cursor.fetchone() or None
    await cursor.close()

    if row and row[0]:
        return row[0].split(",")
    return []