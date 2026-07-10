import logging

from aiogram import Bot
from aiogram.utils.media_group import MediaGroupBuilder

logger = logging.getLogger(__name__)


async def send_post_with_media(
    bot: Bot,
    text: str,
    photos: list,
    markup,
    chat_id: int,
    prefix: str = "",
) -> list[int]:
    """Отправляет пост с медиа или без, используя bot и chat_id напрямую."""
    full_text = f"{prefix}{text}" if prefix else text
    created_ids = []

    if len(photos) == 1:
        file_id = photos[0]
        media_message = await bot.send_photo(
            chat_id=chat_id,
            photo=file_id,
        )

        sent_message = await bot.send_message(
            chat_id=chat_id,
            text=full_text,
            reply_markup=markup,
            parse_mode="HTML"
        )

        created_ids.append(media_message.message_id)
        created_ids.append(sent_message.message_id)

    elif len(photos) > 1:
        builder = MediaGroupBuilder()
        for file_id in photos:
            builder.add_photo(media=file_id)
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
        sent_message = await bot.send_message(
            chat_id=chat_id,
            text=full_text,
            reply_markup=markup,
            parse_mode="HTML"
        )
        created_ids.append(sent_message.message_id)

    return created_ids