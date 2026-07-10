import logging

logger = logging.getLogger(__name__)


async def cleanup_media_messages(bot, chat_id: int, state):
    data = await state.get_data()
    # sent_messages = data.get("sent_message")
    selected_media = data.get("selected_media")

    logger.debug(
        f"sent_messages={selected_media}, "
        f"type={type(selected_media)}, "
        f"len={len(selected_media) if selected_media else 0},"
        f"item_type={type(selected_media[0]) if selected_media and len(selected_media) > 0 else 'None'}"
    )

    if selected_media and len(selected_media) > 0:
        if len(selected_media) == 1:
            logger.info("В списке только 1 сообщение (текст), отмена удаления")
            return

        selected_media.pop(-1)

        if len(selected_media) == 1:
            await bot.delete_message(chat_id=chat_id, message_id=selected_media[0])
            logger.info(f"Одиночное медиа-сообщение {selected_media[0]} было удалено")

        elif len(selected_media) > 1:
            await bot.delete_messages(chat_id=chat_id, message_ids=selected_media)
            logger.info(f"Медиа-сообщения {selected_media} были удалены")

    else:
        logger.info("Функция ---cleanup_media_messages--- список с id сообщений пуст")
