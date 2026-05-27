# сторонние библиотеки
import re
import logging

# с проекта
from AI_SMM_AGENT.app.models.n8n import N8NStatus, N8NResult
from aiogram.types import InputMediaPhoto


logger = logging.getLogger(__name__)


def sort_answer_n8n(payload: dict) -> N8NResult:
    status_str = payload.get("status_generate")
    post = payload.get("post")
    question = payload.get("question")
    reason_reject = payload.get("reason")
    style_warning = payload.get("style_warning") or None # предупреждение о несоответствии стиля
    media_warning = payload.get("media_warning") or None
    selected_file_ids = payload.get("selected_file_ids") or []
    media_assessment = payload.get("media_assessment") or []

    try:
        status = N8NStatus(status_str)
    except ValueError as e:
        logger.error(f"Ошибка : {e} : в функции ---sort_answer_n8n---")
        status = N8NStatus.UNKNOWN

    n8n_object = N8NResult(status=status,
                           post_text=post,
                           question_text=question,
                           reason_reject_text=reason_reject,
                           media_assessment=media_assessment
                           )

    if n8n_object.status == N8NStatus.SUCCESS:
        logger.info("Пользователь получил рекомендацию на публикацию поста")
        text = n8n_object.post_text

    elif n8n_object.status == N8NStatus.REJECTION:
        logger.info("Пользователь не получил рекомендацию на публикацию поста")
        text = f"<b>⚠️ Не рекомендуется к публикации:\n</b> {n8n_object.reason_reject_text}"

    elif n8n_object.status == N8NStatus.QUESTION:
        logger.info("Пользователь получил уточняющий вопрос от агента")
        text = f"<b>Уточняющий вопрос:</b>\n{n8n_object.question_text}"

    else:
        text = "Произошла ошибка, вернитесь в главное меню и попробуйте снова"
        logger.error(f"Ошибка в функции ---sort_answer_n8n--- ответ n8n не получается отфильтровать."
                     f" Answer: {payload}, n8n_object: {n8n_object}")

    style_warning_block = f"⚠️{style_warning}⚠️\n\n\n\n" if style_warning else ""
    media_warning_block = f"⚠️{media_warning}⚠️\n\n\n\n" if media_warning else ""
    text = style_warning_block + media_warning_block + text if style_warning or media_warning_block else text

    text = strip_markdown(text)


    logger.info(f"DEBUG: n8n_object: {n8n_object}, payload: {payload}")  # ======================================= DEBUG
    return N8NResult(status=status,
                     final_text=text,
                     post_text=post,
                     style_warning=style_warning,
                     selected_file_ids=selected_file_ids,
                     media_assessment=media_assessment
                     )


def strip_markdown(text: str) -> str:
    text = re.sub(r'#{1,6}\s*', '', text)        # ### заголовки
    text = re.sub(r'\*\*(.*?)\*\*', r'<b>\1</b>', text)  # **bold** → <b>
    text = re.sub(r'\*(.*?)\*', r'<i>\1</i>', text)      # *italic* → <i>
    text = re.sub(r'^\d+\.\s+', '', text, flags=re.MULTILINE)  # нумерация
    return text.strip()


async def get_telegram_file_url(file_id: str, token: str, bot_object) -> str:
    file = await bot_object.get_file(file_id)
    return f"https://api.telegram.org/file/bot{token}/{file.file_path}"


async def publish_to_channel(bot, channel_id: int, text: str, draft_object: dict):
    media_list = draft_object.get("media", []) if draft_object else []
    selected_ids = draft_object.get("selected_media_ids", []) if draft_object else []

    # Фильтруем только выбранные, сохраняем порядок из selected_ids
    media_index = {m["file_id"]: m for m in media_list}
    selected_media = [media_index[fid] for fid in selected_ids if fid in media_index]

    photos = [m for m in selected_media if m["type"] == "photo"]

    if not photos:
        await bot.send_message(chat_id=channel_id, text=text, parse_mode="HTML")

    elif len(photos) == 1:
        await bot.send_photo(
            chat_id=channel_id,
            photo=photos[0]["file_id"],
            caption=text[:1024],
            parse_mode="HTML"
        )

    else:
        media_group = [InputMediaPhoto(media=p["file_id"]) for p in photos]
        media_group[0].caption = text[:1024]
        media_group[0].parse_mode = "HTML"
        await bot.send_media_group(chat_id=channel_id, media=media_group)


