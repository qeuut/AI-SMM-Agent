# другие
import logging
import uuid


# БД
from AI_SMM_AGENT.app.repositories.database import get_db
from AI_SMM_AGENT.app.repositories.user_info_repo import db_set_id_in_user_info

# models
from AI_SMM_AGENT.app.models.sessions_modes import SessionModes


logger = logging.getLogger(__name__)


async def db_update_session_id(user_id: int) -> bool | str:
    new_session_id = str(user_id) + "_" + str(uuid.uuid4())
    db = await get_db()
    cursor = await db.execute("""
                UPDATE user_info SET session_id = ? WHERE user_id = ?""",
                            (new_session_id, user_id))
    await db.commit()

    if cursor.rowcount == 0:
        logger.warning(
            f"Функция ---db_reset_session_id--- user_id = {user_id}, не найден, значение session_id не было обновлено")
        return False

    else:
        logger.info(f"Функция ---db_reset_session_id--- session_id успешно обновлено на {new_session_id}")
        return new_session_id


async def db_get_session_id(user_id: int) -> bool | str:
    db = await get_db()
    cursor = await db.execute("""
                    SELECT session_id FROM user_info WHERE user_id = ?""", (user_id,))

    row = await cursor.fetchone()

    if not row:
        logger.warning(f"Функция ---get_session_id--- user_id = {user_id} не найдено")
        return False

    session_id = row["session_id"]

    if session_id:
        logger.info(f"Функция ---get_session_id--- было найдено и возвращено значение session_id = {session_id}")
        return session_id

    logger.error("Функция ---get_session_id--- значение session_id не найдено")
    return False


async def get_or_create_session(user_id: int, mode: SessionModes = SessionModes.DEFAULT) -> bool | str | None: # modes: set_session_id, get_session_id
    if not isinstance(user_id, int):
        logger.error("Функция ---ger_or_create_session--- user_id не int")
        return False

    # MODE :: SET_USER_ID
    await db_set_id_in_user_info(user_id)

    # MODE :: GET_SESSION_ID
    if mode == SessionModes.GET_SESSION_ID:

        received_session_id = await db_get_session_id(user_id) # пытаемся получить session_id

        if not received_session_id: # проверяем его на наличие

            received_session_id = await db_update_session_id(user_id) # потом создаем и получаем новый session_id
            if not received_session_id: # если произошла ошибка, то возвращаем False
                return False # если произошла ошибка, то возвращаем False

        return received_session_id # если session_id уже есть, то просто возвращаем уже полученный выше результат

    # MODE :: SET_SESSION_ID
    elif mode == SessionModes.SET_SESSION_ID:
        new_session_id = await db_update_session_id(user_id)
        if not new_session_id:
            return False

        return new_session_id
