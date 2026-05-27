import logging

logger = logging.getLogger(__name__)


async def cleanup_media_messages(bot, chat_id: int, state):
    data = await state.get_data()
    sent_messages = data.get("sent_message")

    logger.warning(f"DEBUG: Сейчас в sent_messages лежит: {sent_messages}")

    if sent_messages:
        sent_messages.pop(-1) # не удаляем текстовую часть потому что она всегда идет последней, а у нас везде edit_text
        await bot.delete_messages(chat_id=chat_id, message_ids=sent_messages)
        logger.info(f"Сообщения {sent_messages} были удалены")

    else:
        logger.info("Функция ---cleanup_media_messages--- список с id сообщений пуст")