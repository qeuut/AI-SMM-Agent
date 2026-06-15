import uuid
import json
import logging

from AI_SMM_AGENT.app.services.database import get_db
from AI_SMM_AGENT.app.models.sessions_modes import SessionModes
from AI_SMM_AGENT.app.models.stat_of_post import ReturnedPostStat

logger = logging.getLogger(__name__)


# async def draft_saving(user_id: int, draft_json: str, time: str) -> int:
#     db = await get_db()
#
#     cursor = await db.execute("""
#             INSERT INTO """)


    #
    #
    # db = await get_db()
    #
    # cursor = await db.execute(f"""
    #         INSERT INTO posts (user_id, draft_json, {at}, status) values(?, ?, ?, ?)""",
    #         (user_id, draft_json, time, status))
    #
    # await db.commit()
    # return cursor.lastrowid