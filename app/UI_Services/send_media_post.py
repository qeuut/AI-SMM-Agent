import logging

# aiogram
from aiogram import Bot
from aiogram.types import CallbackQuery
from aiogram.exceptions import TelegramAPIError
from aiogram.utils.media_group import MediaGroupBuilder

# their own

logger = logging.getLogger(__name__)


async def send_post_with_media(
    bot: Bot,
    text: str,
    photos: list[dict],
    markup,
    prefix: str = "",
    callback: CallbackQuery | None = None,
    media_already_sent: bool = True,
    chat_id: int | None = None
) -> list[int]:
    """Удаляет текущее сообщение и отправляет пост с медиа или без."""
    full_text = f"{prefix}{text}" if prefix else text
    created_ids = []

    try:
        await callback.message.delete()
    except TelegramAPIError:
        pass

    if len(photos) == 1 and not media_already_sent:
        logger.info("Была получена 1 фотография")
        sent_message = await callback.message.answer_photo(
            photo=photos[0]["file_id"],
            caption=full_text[:1024],
            reply_markup=markup,
            parse_mode="HTML"
        )
        created_ids.append(sent_message.message_id)

    elif len(photos) > 1 and not media_already_sent:
        logger.info("было получено более 1 фотографии")
        builder = MediaGroupBuilder()
        for p in photos:
            builder.add_photo(media=p["file_id"])

        media_messages = await bot.send_media_group(chat_id=chat_id, media=builder.build())
        created_ids.extend([msg.message_id for msg in media_messages])
        text_message = await bot.send_message(
            chat_id=chat_id,
            text=full_text,
            reply_markup=markup,
            parse_mode="HTML"
        )
        created_ids.append(text_message.message_id)

    else:
        logger.info("Фотографий не было найдено")
        sent_message = await callback.message.answer(
            text=full_text,
            reply_markup=markup,
            parse_mode="HTML"
        )
        created_ids.append(sent_message.message_id)

    return created_ids