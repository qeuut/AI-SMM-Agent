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
    text = (
        "<b>💡 Контент-план</b>\n\n"

        "Бот поможет составить пошаговую контент-стратегию для вашего канала на неделю или месяц вперед.\n\n"

        "<b>Что умеет система:</b>\n"
        "» Генерировать рубрики и конкретные темы для публикаций\n"
        "» Распределять посты по дням недели для удержания аудитории\n"
        "» Адаптировать идеи под тематику и Tone of Voice вашего бренда\n\n"

        "<blockquote>Для точной настройки вы можете загрузить описание вашего канала или примеры старых постов в разделе «Стиль бренда».</blockquote>\n\n"

        "Введите ключевую тему, нишу вашего канала или пришлите краткое описание идеи для генерации контент-плана... 🤖"
    )

    await callback.message.edit_text(text=text,reply_markup=back_to(), parse_mode="HTML")
