import logging
from AI_SMM_AGENT.app.repositories.database import get_db

logger = logging.getLogger(__name__)


async def db_set_id_in_user_info(user_id) -> None:
    db = await get_db()
    await db.execute("""
                INSERT OR IGNORE INTO user_info (user_id) VALUES(?)""",
                    (user_id,))
    await db.commit()


async def save_channel_id(channel_id: int, user_id: int) -> None:
    db = await get_db()
    await db.execute("""
                UPDATE user_info SET channel_id = ? WHERE user_id = ?""",
                     (channel_id, user_id))
    await db.commit()