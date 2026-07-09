import logging
import pydantic


from typing import Optional


from AI_SMM_AGENT.app.bot import settings
from AI_SMM_AGENT.app.models.draft import MediaInput, MediaType
from AI_SMM_AGENT.app.models.data_models import DraftPost
from AI_SMM_AGENT.app.services.post_service import get_telegram_file_url
from AI_SMM_AGENT.app.keyboards import back_to


from aiogram.types import Message
from aiogram.fsm.context import FSMContext


logger = logging.getLogger(__name__)


async def post_data_preparation(message: Message, state: FSMContext, album: Optional[list[Message]]) -> any:
    try:
        data = await state.get_data()
        raw = data.get("draft_post")
        edit_mode = data.get("edit_mode", False)
        draft = DraftPost() if raw is None else DraftPost.model_validate(raw)
        messages_to_process = album if album else [message]

    except pydantic.ValidationError as e:
        logger.exception(f"Ошибка валидации в catch_all: {e}")
        await message.answer("Ошибка в записи черновика. Попробуйте отправить заново.", reply_markup=back_to())
        await state.update_data(draft_post=None)
        return
    except Exception as e:
        logger.exception(f"Неизвестная ошибка в catch_all: {e}")
        await message.answer("Ошибка в записи черновика. Попробуйте отправить заново.", reply_markup=back_to())
        await state.update_data(draft_post=None)
        return

    media_items = []
    for msg in messages_to_process:
        if msg.photo:
            url = await get_telegram_file_url(file_id=msg.photo[-1].file_id, token=settings.BOT_TOKEN, bot_object=message.bot)
            media_items.append(MediaInput(type=MediaType.PHOTO, file_id=msg.photo[-1].file_id, caption=msg.caption, url=url))

        elif msg.video:
            url = await get_telegram_file_url(file_id=msg.video.file_id, token=settings.BOT_TOKEN, bot_object=message.bot)
            media_items.append(MediaInput(type=MediaType.VIDEO, file_id=msg.video.file_id, caption=msg.caption, url=url))

        elif msg.voice:
            url = await get_telegram_file_url(file_id=msg.voice.file_id, token=settings.BOT_TOKEN, bot_object=message.bot)
            media_items.append(MediaInput(type=MediaType.VOICE, file_id=msg.voice.file_id, caption=msg.caption, url=url))

        elif msg.text:
            media_items.append(MediaInput(type=MediaType.TEXT, text=msg.text))

    return edit_mode, media_items, draft # bool, List, DraftPost