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

    if sent_messages and len(sent_messages) > 0:
        if len(sent_messages) == 1:
            logger.info("В списке только 1 сообщение (текст), отмена удаления")
            return

        sent_messages.pop(-1)

        if len(sent_messages) == 1:
            await bot.delete_message(chat_id=chat_id, message_id=sent_messages[0])
            logger.info(f"Одиночное медиа-сообщение {sent_messages[0]} было удалено")

        elif len(sent_messages) > 1:
            await bot.delete_messages(chat_id=chat_id, message_ids=sent_messages)
            logger.info(f"Медиа-сообщения {sent_messages} были удалены")

    else:
        logger.info("Функция ---cleanup_media_messages--- список с id сообщений пуст")
