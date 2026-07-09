import json
import logging

from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

from datetime import datetime
from zoneinfo import ZoneInfo

from AI_SMM_AGENT.app.models.data_models import DraftPost
from AI_SMM_AGENT.app.keyboards.general_inline import publishing_post
from AI_SMM_AGENT.app.services.post_service import publish_to_channel
from AI_SMM_AGENT.app.bot import settings
from AI_SMM_AGENT.app.repositories.post_repo import db_created_post


logger = logging.getLogger(__name__)


async def publish_generated_post(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    generated_text = data.get("generated_text")
    moscow_time = datetime.now(ZoneInfo("Europe/Moscow"))


    if generated_text is None:
        logger.error("Пост утерян в cmd_publishing_post — generated_text = None")
        await callback.message.answer("Произошла ошибка, пост не сохранён. Попробуйте снова.",
                                      reply_markup=publishing_post())
        return

    draft = DraftPost.model_validate(data.get("draft_post"))
    post_record = json.dumps({
        "text": generated_text,
        "selected_media_ids": draft.selected_media_ids
    }, ensure_ascii=False)

    published_ids = await publish_to_channel(
        bot=callback.bot,
        channel_id=settings.CHANNEL_ID,
        text=generated_text,
        draft_object=data.get("draft_post")
    )

    post_id = await db_created_post(
        user_id=callback.from_user.id,
        draft_json=post_record,
        at="published_at",
        status="published",
        time=moscow_time.strftime("%Y-%m-%d %H:%M:%S"),
        message_ids=published_ids
    )

    return post_id