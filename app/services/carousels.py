import logging
from AI_SMM_AGENT.app.models.carousels import CarouselResponse


logger = logging.getLogger(__name__)


EMOJI_STATUS = {
    "draft": "📝 Черновик",
    "scheduled": "⏳ Запланирован",
    "published": "✅ Опубликован",
    "error": "⚠️ Ошибка"
}


def get_carousel_page_preview(data: CarouselResponse) -> dict:
    status_text = EMOJI_STATUS.get(data.post.status, data.post.status)

    has_no_media = (
            len(data.post.selected_media_ids) == 0
            and (data.post.published_msg_ids == "" or data.post.published_msg_ids == "None")
    )

    media_status = "❌ Отсутствует" if has_no_media else "📸 Присутствует"

    text_back = "⬅️ Назад"
    text_forward = "Вперед ➡️"

    callback_data_back = f"carousel_post_{data.post.status}_{data.current_page-1}"
    callback_data_forward = f"carousel_post_{data.post.status}_{data.current_page+1}"

    if data.current_page == 1:
        text_back = "· "
        callback_data_back = "-,-"

    if data.current_page == data.total_count or data.total_count == 0:
        text_forward = " ·"
        callback_data_forward = "-/-"

    inline_texts = [
        text_back,
        f"{data.current_page} / {data.total_count}",
        text_forward,
        "DEBUG: ❌ Удалить пост",
        "⬅️ Вернуться в меню публикаций"
    ]

    inline_callbacks = [
        callback_data_back,
        "-",
        callback_data_forward,
        "-",
        "publication"
    ]

    logger.debug(f"callback_data_back = {callback_data_back}\n callback_data_forward = {callback_data_forward}")

    return {
        "final_text": (
            f"📋 <b>Просмотр публикации [ {data.current_page} из {data.total_count} ]</b>\n\n"
            f"🔹 <b>Статус:</b> {status_text}\n"
            f"📅 <b>Дата публикации:</b> {data.post.date}\n"
            f"🆔 <b>ID Поста:</b> <code>#{data.post.post_id}</code>\n"
            f"────────────────────\n" # придумать что-то с UI под телефон
            f"<b>Текст поста:</b>\n\n"
            f"{data.post.text}\n"
            f"────────────────────\n" # придумать что-то с UI под телефон
            f"📁 <b>Прикрепленный контент:</b> \n{media_status}"
        ),
        "texts": inline_texts,
        "callbacks": inline_callbacks
    }
