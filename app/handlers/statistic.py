# Стандартные библиотеки
import logging

# Сторонние библиотеки
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery

# Клавиатуры
from AI_SMM_AGENT.app.keyboards.general_inline import (
    statistics_info_btn, create_buttons
)
from AI_SMM_AGENT.app.keyboards import (
    back_to,
)
# модели
from AI_SMM_AGENT.app.models.callbacks import CallbacksStatistic
from AI_SMM_AGENT.app.models.stat_of_post import ReturnedPostStat
from AI_SMM_AGENT.app.repositories.post_repo import get_all_posts

# utils
from AI_SMM_AGENT.app.utils.formatters import format_statistics_text

# текста
from AI_SMM_AGENT.app.texts.statistics import STATISTICS_NO_POST_TEXT
statistic_router = Router()


logger = logging.getLogger(__name__)


@statistic_router.callback_query(F.data == CallbacksStatistic.STATISTICS)
async def show_statistics(callback: CallbackQuery):
    # Получаем данные из БД в виде Pydantic-модели
    post_statistics = await get_all_posts(callback.from_user.id)

    # Если у пользователя вообще нет постов в базе
    if not post_statistics:
        await callback.message.edit_text(
            text=STATISTICS_NO_POST_TEXT,
            reply_markup=create_buttons(
                texts=["✨ Создать пост","⬅️ Вернуться в главное меню"],
                callbacks=["create_post","MainMenu"]),
            parse_mode="HTML")
        return

    final_text = format_statistics_text(post_statistics=post_statistics)
    await callback.message.edit_text(final_text, parse_mode="HTML", reply_markup=back_to())




# @statistic_router.callback_query(F.data == CallbacksStatistic.STATISTICS_OF_THIRTY_DAYS)
# async def stat_of_thirty_days(callback: CallbackQuery, state: FSMContext):
#     await callback.message.edit_text("DEBUG: Тут будет статистика за последние 30 дней",
#                                   reply_markup=back_to(text="⬅️ Вернуться в меню статистики", callback_data="statistics"))
#
#
#
# @statistic_router.callback_query(F.data == CallbacksStatistic.STATISTICS_OF_SPECIFIC_POST)
# async def stat_of_specific_post(callback: CallbackQuery, state: FSMContext):
#     await callback.message.edit_text("DEBUG: Тут будет статистика по конкретному посту",
#                                   reply_markup=back_to(text="⬅️ Вернуться в меню статистики", callback_data="statistics"))
#
#
# @statistic_router.callback_query(F.data == CallbacksStatistic.STATISTICS_AI_RECOMMENDATION)
# async def stat_ai_recommendation(callback: CallbackQuery, state: FSMContext):
#     await callback.message.edit_text("DEBUG: Тут будут рекомендации от ваших ИИ-агентов",
#                                   reply_markup=back_to(text="⬅️ Вернуться в меню статистики", callback_data="statistics"))
#







