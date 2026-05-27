# Стандартные библиотеки
import logging

# Сторонние библиотеки
from aiogram import Router, F
from aiogram.types import CallbackQuery

# Клавиатуры
from AI_SMM_AGENT.app.keyboards import (
    back_to
)

# модели
from AI_SMM_AGENT.app.models.callbacks import CallbacksContentPlan


content_plan_router = Router()


logger = logging.getLogger(__name__)


@content_plan_router.callback_query(F.data == CallbacksContentPlan.CONTENT_PLAN)
async def content_plan(callback: CallbackQuery) -> None:
    await callback.message.edit_text(text="DEBUG: здесь будет что то про контент план",reply_markup=back_to())
