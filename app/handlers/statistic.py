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

statistic_router = Router()


logger = logging.getLogger(__name__)


@statistic_router.callback_query(F.data == CallbacksStatistic.STATISTICS)
async def show_statistics(callback: CallbackQuery):
    # Получаем данные из БД в виде Pydantic-модели
    stats = await get_all_posts(callback.from_user.id)

    # Если у пользователя вообще нет постов в базе
    if not stats:
        text = (
            "<b>📊 Статистика и аналитика</b>\n\n"

            "У вас пока нет созданных публикаций.\n\n"

            "Как только вы сгенерируете первый материал, искусственный интеллект начнет собирать аналитику, "
            "и покажет общую статистику вашего контента.\n\n"

            "<blockquote>Создайте свой первый пост прямо сейчас, чтобы открыть этот раздел!</blockquote>"
        )

        await callback.message.edit_text(
            text=text,
            reply_markup=create_buttons(
                texts=["✨ Создать пост","⬅️ Вернуться в главное меню"],
                callbacks=["create_post","MainMenu"]),
            parse_mode="HTML")
        return

    fmt = "%d.%m.%Y %H:%M"
    last_date = (
        stats.last_post_date.strftime(fmt) if stats.last_post_date else "—"
    )
    scheduled_date = (
        stats.last_scheduled_post_date.strftime(fmt)
        if stats.last_scheduled_post_date
        else "Нет"
    )
    published_date = (
        stats.last_published_post_date.strftime(fmt)
        if stats.last_published_post_date
        else "Нет"
    )

    text = (
        "<b>📊 Статистика канала</b>\n\n"
        "В этом разделе вы можете оценить эффективность вашего контента, "
        "посмотреть охваты и получить персональные советы от искусственного "
        "интеллекта по улучшению показателей.\n\n"
        "<b>📈 Общие показатели:</b>\n"
        f"- Всего постов сгенерировано: <code>{stats.quantity_posts}</code>\n"
        f"- Сейчас запланировано: <code>{stats.quantity_scheduled}</code>\n"
        f"- Уже опубликовано: <code>{stats.quantity_published}</code>\n\n"
        "<b>📝 Последняя активность:</b>\n"
        f"- Текст: <i>«{stats.last_post_about}»</i>\n"
        f"- Статус: <b>{stats.last_post_status}</b>\n"
        f"- Дата изменения: <code>{last_date}</code>\n\n"
        "<b>📅 Даты последних выходов:</b>\n"
        f"- Крайний в очереди: <code>{scheduled_date}</code>\n"
        f"- Последний вышедший: <code>{published_date}</code>\n\n"
    )

    await callback.message.edit_text(text, parse_mode="HTML", reply_markup=back_to())

    # await callback.message.edit_text(text=text,
    #                                  reply_markup=statistics_info_btn(),
    #                                  parse_mode="HTML")


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







