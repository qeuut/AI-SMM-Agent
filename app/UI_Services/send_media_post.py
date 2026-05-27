# third parties


# aiogram
from aiogram.types import CallbackQuery
from aiogram.exceptions import TelegramAPIError
from aiogram.utils.media_group import MediaGroupBuilder

# their own


async def send_post_with_media(
    callback: CallbackQuery,
    text: str,
    photos: list[dict],
    markup,
    prefix: str = "",
    media_already_sent: bool = True
) -> list[int]:
    """Удаляет текущее сообщение и отправляет пост с медиа или без."""
    full_text = f"{prefix}{text}" if prefix else text
    created_ids = []

    try:
        await callback.message.delete()
    except TelegramAPIError:
        pass

    if len(photos) == 1 and not media_already_sent:
        sent_message = await callback.message.answer_photo(
            photo=photos[0]["file_id"],
            caption=full_text[:1024],
            reply_markup=markup,
            parse_mode="HTML"
        )
        created_ids.append(sent_message.message_id)

    elif len(photos) > 1 and not media_already_sent:
        builder = MediaGroupBuilder()
        for p in photos:
            builder.add_photo(media=p["file_id"])

        media_messages = await callback.message.answer_media_group(media=builder.build())
        created_ids.extend([msg.message_id for msg in media_messages])
        text_message = await callback.message.answer(
            text=full_text,
            reply_markup=markup,
            parse_mode="HTML"
        )
        created_ids.append(text_message.message_id)

    else:
        sent_message = await callback.message.answer(
            text=full_text,
            reply_markup=markup,
            parse_mode="HTML"
        )
        created_ids.append(sent_message.message_id)

    return created_ids