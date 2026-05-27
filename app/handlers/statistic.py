# Стандартные библиотеки
import logging

# Сторонние библиотеки
from aiogram import Router, F
from aiogram.types import CallbackQuery

# Клавиатуры
from AI_SMM_AGENT.app.keyboards.general_inline import (
    statistics_info_btn
)

# модели
from AI_SMM_AGENT.app.models.callbacks import CallbacksStatistic

statistic_router = Router()


logger = logging.getLogger(__name__)


@statistic_router.callback_query(F.data == CallbacksStatistic.STATISTICS)
async def statistic_info(callback: CallbackQuery) -> None:
    text = (
        "<b>📊 Статистика</b>\n\n"
        "В этом разделе вы можете оценить эффективность вашего контента, "
        "посмотреть охваты и получить персональные советы от искусственного "
        "интеллекта по улучшению показателей канала.\n\n"
        "Выберите формат аналитики:"
    )

    await callback.message.edit_text(text=text,
                                     reply_markup=statistics_info_btn(),
                                     parse_mode="HTML")