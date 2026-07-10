import json
import logging

from AI_SMM_AGENT.app.repositories.database import get_db
from AI_SMM_AGENT.app.models.stat_of_post import ReturnedPostStat
from AI_SMM_AGENT.app.models.carousels import CarouselResponse, CarouselPostData


logger = logging.getLogger(__name__)


async def db_created_post(user_id: int, draft_json: str, time: str | None, status: str, at: str = "", message_ids: list[int] | None = None) -> int:
    if at not in ["created_at", "scheduled_at", "published_at"]:
        logger.error("Аргумент ---at--- в функции ---db_created_post--- не равен ожидаемому значению. Взято значение: created_at")
        at = "created_at"

    db = await get_db()

    channel_message_id = json.dumps(message_ids)

    cursor = await db.execute(f"""
            INSERT INTO posts (user_id, draft_json, {at}, status, message_ids) values(?, ?, ?, ?, ?)""",
            (user_id, draft_json, time, status, channel_message_id))

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

    # счетчики и переменные для дат
    quantity_scheduled = 0
    quantity_published = 0
    last_scheduled_post_date = None
    last_published_post_date = None

    for row in rows:
        if row["status"] == "scheduled":
            quantity_scheduled += 1
            last_scheduled_post_date = row["scheduled_at"]

        if row["status"] == "published":
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


async def cancel_schedule_post(user_id: int, post_id: int) -> bool:
    if not user_id or not post_id:
        logger.error("Функция ---cancel_post--- не передан один из аргументов")
        return False

    db = await get_db()
    cursor = await db.execute(
        "DELETE FROM posts WHERE user_id = ? AND post_id = ?", (user_id, post_id)
    )

    await db.commit()

    if cursor.rowcount > 0:
        logger.info(f"---cancel_post--- Успешно удален пост ID: {post_id} для user_id: {user_id}")

    else:
        logger.error(f"---cancel_post--- Пост ID: {post_id} не был удален для {user_id}")
        return False

    return True


async def get_channel_message_ids(user_id: int, post_id: int) -> list[int]:
    db = await get_db()
    cursor = await db.execute(
        "SELECT message_ids FROM posts WHERE user_id = ? AND post_id = ?",
        (user_id, post_id)
    )
    row = await cursor.fetchone()
    if not row or not row["message_ids"]:
        return []
    return json.loads(row["message_ids"])


async def get_carousel_data_from_db(user_id: int, current_page: int, status: str) -> CarouselResponse:
    db = await get_db() # получаем соединение

    cursor = await db.execute(
        "SELECT COUNT(*) FROM posts WHERE user_id = ? AND status = ?", (user_id, status) # получаем количество строк с таблицы posts
    )
    res = await cursor.fetchone() # получаем количество постов
    total_count = res[0] if res else 0 # если нет постов то cursor.fetchone() вернет (0,) 0 - False

    offset = current_page - 1 # показатель сколько постов нужно всего пропустить прежде чем показать нужный (для 3-го поста offset = 2 для 4 offset = 3 для 2 offset = 1)

    cursor = await db.execute(
        "SELECT * FROM posts WHERE user_id = ? AND status = ? ORDER BY created_at DESC LIMIT 1 OFFSET ?", # достаем пост по убыванию времени
        (user_id, status, offset)
    )
    row = await cursor.fetchone() # получаем строку с нужным постом

    if row: # если пост есть
        post = CarouselResponse.parse_row_to_post(row) # парсим строку с постом sqlite (структура row)
    else: # если нет, то заполняем модель как в сценарии ошибки
        post = CarouselPostData(
            post_id=0, user_id=user_id, status="error", date="-", text="Пост не найден",
            published_msg_ids="", selected_media_ids=[]
        )

    return CarouselResponse(
        total_count=total_count,
        current_page=current_page,
        post=post
    )