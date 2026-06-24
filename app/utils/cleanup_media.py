import logging

logger = logging.getLogger(__name__)


async def cleanup_media_messages(bot, chat_id: int, state):
    data = await state.get_data()
    sent_messages = data.get("sent_message")


    logger.debug(
        f"sent_messages={sent_messages}, "
        f"type={type(sent_messages)}, "
        f"len={len(sent_messages) if sent_messages else 0},"
        f"item_type={type(sent_messages[0]) if sent_messages and len(sent_messages) > 0 else 'None'}"
    )

    if sent_messages:
        sent_messages.pop(-1) # не удаляем текстовую часть потому что она всегда идет последней, а у нас везде edit_text
        await bot.delete_messages(chat_id=chat_id, message_ids=sent_messages) # sent_messages
        logger.info(f"Сообщения {sent_messages} были удалены")

    else:
        logger.info("Функция ---cleanup_media_messages--- список с id сообщений пуст")