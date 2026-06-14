# Стандартные библиотеки
import logging
import json
from itertools import count

# Сторонние библиотеки
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext
from aiogram.filters import StateFilter

# Клавиатуры
from AI_SMM_AGENT.app.keyboards.general_inline import (
    publication_main, manage_current_post, y_or_n,
    cancel_or_back, create_post_or_back,
)
from AI_SMM_AGENT.app.keyboards import back_to, create_buttons

# Репозитории
from AI_SMM_AGENT.app.repositories.post_repo import db_created_post

# Модели
from AI_SMM_AGENT.app.models.callbacks import CallbacksPublication, CallbacksPost
from AI_SMM_AGENT.app.utils.states import SchedulePost

# Сервисы
from AI_SMM_AGENT.app.services.database import get_db

# Utils
from AI_SMM_AGENT.app.utils.cleanup_media import cleanup_media_messages
from AI_SMM_AGENT.app.utils.parsing_time import parse_schedule_time

publication_router = Router()
logger = logging.getLogger(__name__)


@publication_router.callback_query(F.data == CallbacksPublication.PUBLICATION)
async def publication(callback: CallbackQuery) -> None:
    logger.info(f"Пользователь {callback.from_user.id} открыл раздел публикаций")
    text = (
        "<b>🗂️ Управление публикациями</b>\n\n"
        "Здесь вы можете отслеживать статус ваших постов, планировать "
        "выход нового контента на будущее или просматривать историю "
        "уже опубликованных записей.\n\n"
    )
    await callback.message.edit_text(text=text, reply_markup=publication_main(), parse_mode="HTML")


@publication_router.callback_query(F.data == CallbacksPublication.SCHEDULED_POST)
async def cmd_schedule_post(callback: CallbackQuery, state: FSMContext, bot: Bot):
    text_no_active_post = (
        "<b>📅 Планирование публикаций</b>\n\n"

        "В системе пока нет активного черновика для отправки.\n\n"

        "<b>Как запланировать пост по таймеру:</b>\n"
        "» Нажмите на кнопку <b>✨ Создать пост</b> ниже и отправьте материалы;\n"
        "» Дождитесь создания готового текста системой;\n"
        "» Нажмите кнопку «Запланировать» под результатом и напишите время.\n\n"

        "<i>Создайте свой первый материал прямо сейчас, чтобы поставить его в контент-очередь.</i>"
    )

    logger.info(f"Пользователь {callback.from_user.id} нажал 'Запланировать'")
    data = await state.get_data()
    generated_text = data.get("generated_text")
    draft_post = data.get("draft_post")

    if generated_text and draft_post:
        logger.info(f"Пользователь {callback.from_user.id} — активный пост найден, переходим к вводу времени")
        await state.update_data(media_sent=False)
        await cleanup_media_messages(bot=bot, chat_id=callback.message.chat.id, state=state)
        await callback.message.edit_text(
            "Напишите удобное время для публикации.\n\n"
            "Например: <i>завтра в 15:00</i>, <i>в среду вечером</i>, <i>25 июня в 18:30</i>",
            reply_markup=back_to(text="⬅️ Вернуться в меню публикаций", callback_data="publication"),
            parse_mode="HTML"
        )
        await state.set_state(SchedulePost.WaitScheduleTime)

    else:
        logger.warning(f"Пользователь {callback.from_user.id} — активный пост не найден в FSM")
        await callback.message.edit_text(
            text=text_no_active_post,
            reply_markup=create_post_or_back(),
            parse_mode="HTML"
        )


@publication_router.message(StateFilter(SchedulePost.WaitScheduleTime))
async def get_time_for_plan(message: Message, state: FSMContext):
    logger.info(f"Пользователь {message.from_user.id} ввёл время: '{message.text}'")
    data = await state.get_data()
    generated_text = data.get("generated_text")
    draft_dict = data.get("draft_post")
    scheduled_in_eny_case = data.get("scheduled_in_eny_case")

    if not generated_text:
        logger.error(f"Пользователь {message.from_user.id} — generated_text пропал из FSM в get_time_for_plan")
        await message.answer("Нет активного поста для планирования.", reply_markup=back_to())
        return

    logger.info(f"Пользователь {message.from_user.id} — отправляем запрос на парсинг времени")
    result = await parse_schedule_time(message.text)
    logger.info(f"Пользователь {message.from_user.id} — результат парсинга: {result}")

    if result.get("datetime") is None:
        question = result.get("question", "Не могу разобрать время, уточните пожалуйста")
        logger.warning(f"Пользователь {message.from_user.id} — время не распознано, задаём вопрос: {question}")
        await message.answer(f"Уточните: {question}")
        return

    scheduled_time = result["datetime"]
    logger.info(f"Пользователь {message.from_user.id} — распознанное время: {scheduled_time}")

    # проверка конфликта
    db = await get_db()
    cursor = await db.execute(
        "SELECT draft_json FROM posts WHERE user_id = ? AND scheduled_at = ? AND status = 'scheduled'",
        (message.from_user.id, scheduled_time)
    )
    conflict = await cursor.fetchone()

    if conflict and not scheduled_in_eny_case:
        conflict_data = json.loads(conflict["draft_json"])
        preview = conflict_data.get("text", "")[:60]
        logger.warning(
            f"Пользователь {message.from_user.id} — конфликт времени {scheduled_time}, "
            f"существующий пост: '{preview}...'"
        )
        await message.answer(
            f"⚠️ На это время уже запланирован пост:\n\n<i>{preview}...</i>\n\nВы уверены что хотите запланировать "
            f"2 поста на одно и тоже время?.", # могут быть и 2 и 3+ поста на одно и тоже время - сменить форматирование
            # текста под 2+ поста и предупреждение об этом например: на это время уже запланировано (количество постов)
            #вы уверены, что хотите запланировать (количество+1) пост?
            parse_mode="HTML",
            reply_markup=y_or_n(callbacks=[CallbacksPublication.YES_ANSWER, CallbacksPost.SHOW_POST])
        )
        return

    draft_json = json.dumps({
        "text": generated_text,
        "selected_media_ids": draft_dict.get("selected_media_ids", []) if draft_dict else []
    }, ensure_ascii=False)

    await db_created_post(
        user_id=message.from_user.id,
        draft_json=draft_json,
        at="scheduled_at",
        status="scheduled",
        time=scheduled_time
    )

    logger.info(f"Пользователь {message.from_user.id} — пост записан в БД со статусом scheduled на {scheduled_time}")
    await state.update_data(post_state="scheduled")
    await message.answer(
        f"✅ Пост запланирован на <b>{scheduled_time}</b>",
        reply_markup=cancel_or_back(),
        parse_mode="HTML"
    )

@publication_router.callback_query(F.data == CallbacksPublication.YES_ANSWER)
async def set_fsm_for_y_answer(callback: CallbackQuery, state: FSMContext):
    await state.update_data(scheduled_in_eny_case=True)
    await get_time_for_plan(message=callback.message, state=state)


@publication_router.callback_query(F.data == CallbacksPublication.QUEUE_PUBLICATION)
async def queue_posts(callback: CallbackQuery, state: FSMContext) -> None:
    text_queue_is_none = (
        "<b>📋 Очередь публикаций</b>\n\n"
    
        "В вашем контент-плане пока нет запланированных постов.\n\n"
    
        "<blockquote>Все созданные вами публикации, которые ожидают отправки по таймеру, "
        "будут отображаться в этом разделе в виде удобного списка с датой и временем.</blockquote>\n\n"
    
        "<i>Хотите заполнить очередь контентом? Начните генерацию нового материала прямо сейчас.</i>"
    )

    logger.info(f"Пользователь {callback.from_user.id} открыл очередь публикаций")

    db = await get_db()
    cursor = await db.execute(
        "SELECT post_id, draft_json, scheduled_at FROM posts "
        "WHERE user_id = ? AND status = 'scheduled' "
        "ORDER BY scheduled_at ASC",
        (callback.from_user.id,)
    )
    rows = await cursor.fetchall()

    if not rows:
        logger.error("Функция ---queue_posts--- rows - пуст")
        await callback.message.edit_text(text=text_queue_is_none,
                                         reply_markup=create_buttons(texts=["✨ Создать пост",
                                                                            "⬅️ Вернуться в меню публикаций"],
                                                                     callbacks=["create_post", "publication"]),
                                         parse_mode="HTML")
        return None

    result = ""
    counting = 1

    for row in rows:
        draft_json = row[1]
        parse_json = json.loads(draft_json)
        first_sixty_symbols = parse_json["text"][:60] + "..."
        scheduled_at = row[2]
        result_string = f"{counting}. {scheduled_at} — {first_sixty_symbols}"
        counting += 1
        result += "\n\n" + result_string

    await callback.message.edit_text(text=result+"\n\n\nЕсли вас интересует конкретный пост то напишите его порядковый "
                                                 "номер для того что бы узнать подробности про него",
                                     reply_markup=back_to(text="⬅️ Вернуться назад",callback_data="publication"))

@publication_router.callback_query(F.data == CallbacksPublication.PUBLISHED_POST)
async def check_published_posts(callback: CallbackQuery):
    logger.info(f"Пользователь {callback.from_user.id} открыл историю опубликованных постов")
    await callback.message.edit_text(
        "DEBUG: тут можно будет посмотреть опубликованные посты (список со статистикой)",
        reply_markup=back_to(text="⬅️ Вернуться в меню публикаций", callback_data="publication")
    )