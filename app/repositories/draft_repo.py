import logging

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