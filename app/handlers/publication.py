# Стандартные библиотеки
import logging
import json

# Сторонние библиотеки
from aiogram import Router, F, Bot
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.context import FSMContext

from AI_SMM_AGENT.app.handlers.posts import show_post
# Клавиатуры
from AI_SMM_AGENT.app.keyboards.general_inline import (
    publication_main, y_or_n_for_sync_post,
    cancel_or_back, create_post_or_back, y_or_n_for_cancel_post
)
from AI_SMM_AGENT.app.keyboards import back_to, create_buttons

# Репозитории
from AI_SMM_AGENT.app.repositories.post_repo import db_created_post
from AI_SMM_AGENT.app.repositories.post_repo import cancel_schedule_post
from AI_SMM_AGENT.app.repositories.post_repo import get_carousel_data_from_db

# Модели
from AI_SMM_AGENT.app.models.callbacks import CallbacksPublication, CallbacksPost
from AI_SMM_AGENT.app.utils.states import SchedulePost

# Сервисы
from AI_SMM_AGENT.app.repositories.database import get_db
from AI_SMM_AGENT.app.services.carousels import get_carousel_page_preview

# Utils
from AI_SMM_AGENT.app.utils.cleanup_media import cleanup_media_messages
from AI_SMM_AGENT.app.utils.parsing_time import parse_schedule_time

# текста
from AI_SMM_AGENT.app.texts.publication_texts import TEXT_QUEUE_IS_NONE, PUBLISHED_IS_NONE, TEXT_NO_ACTIVE_POST, PUBLICATION_MANAGEMENT

publication_router = Router()
logger = logging.getLogger(__name__)


@publication_router.callback_query(F.data == CallbacksPublication.PUBLICATION)
async def publication(callback: CallbackQuery) -> None:
    logger.info(f"Пользователь {callback.from_user.id} открыл раздел публикаций")
    await callback.message.edit_text(text=PUBLICATION_MANAGEMENT, reply_markup=publication_main(), parse_mode="HTML")


@publication_router.callback_query(F.data == CallbacksPublication.SCHEDULED_POST)
async def cmd_schedule_post(callback: CallbackQuery, state: FSMContext, bot: Bot):
    logger.info(f"Пользователь {callback.from_user.id} нажал 'Запланировать'")
    data = await state.get_data()
    generated_text = data.get("generated_text")
    draft_post = data.get("draft_post")

    if generated_text and draft_post:
        logger.info(f"Пользователь {callback.from_user.id} - активный пост найден, переходим к вводу времени")
        await state.update_data(media_sent=False, edit_mode=True) # edit_mode=True - для show_post обновляем, а не шлем новое
        await cleanup_media_messages(bot=bot, chat_id=callback.message.chat.id, state=state)
        await callback.message.edit_text(
            text="Напишите удобное время для публикации.\n\n"
            "Например: <i>завтра в 15:00</i>, <i>в среду вечером</i>, <i>25 июня в 18:30</i>",
            reply_markup=back_to(text="⬅️ Вернуться назад", callback_data="show_post"),
            parse_mode="HTML"
        )
        await state.set_state(SchedulePost.WaitScheduleTime)

    else:
        logger.warning(f"Пользователь {callback.from_user.id} — активный пост не найден в FSM")
        await callback.message.edit_text(
            text=TEXT_NO_ACTIVE_POST,
            reply_markup=create_post_or_back(),
            parse_mode="HTML"
        )


@publication_router.message(SchedulePost.WaitScheduleTime)
async def get_time_for_plan(message: Message, state: FSMContext):
    logger.info(f"Пользователь {message.from_user.id} ввёл время: '{message.text}'")
    data = await state.get_data()
    generated_text = data.get("generated_text")
    draft_dict = data.get("draft_post")
    scheduled_in_eny_case = data.get("scheduled_in_eny_case")
    context = data.get("context")

    user_message = message.text

    if not context:
        context = [user_message]

    else:
        context.append(user_message)

    await state.update_data(context=context)

    if not generated_text:
        logger.error(f"Пользователь {message.from_user.id} — generated_text пропал из FSM в get_time_for_plan")
        await message.answer("Нет активного поста для планирования.", reply_markup=back_to())
        return

    logger.info(f"Пользователь {message.from_user.id} — отправляем запрос на парсинг времени")
    logger.info(f"Отправляю запрос в parse_schedule_time с контекстом: {context}")
    result = await parse_schedule_time(user_message, context) # добавить контекст через FSM
    logger.info(f"Пользователь {message.from_user.id} — результат парсинга: {result}")


    if result.get("datetime") is None:
        question = result.get("question", "Не могу разобрать время, уточните пожалуйста")
        context.append(question)  #- сохраняем вопрос модели к запросам юзера
        await state.update_data(context=context)
        logger.warning(f"Пользователь {message.from_user.id} — время не распознано, задаём вопрос: {question}")
        await message.answer(f"Уточните: {question}", reply_markup=back_to(text="⬅️ Вернуться назад",
                                                                                callback_data="schedule_post"))
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
            reply_markup=y_or_n_for_sync_post(callbacks=[CallbacksPublication.YES_ANSWER, CallbacksPost.SHOW_POST])
        )
        return

    draft_json = json.dumps({
        "text": generated_text,
        "selected_media_ids": draft_dict.get("selected_media_ids", []) if draft_dict else []
    }, ensure_ascii=False)

    post_id = await db_created_post(
                   user_id=message.from_user.id,
                   draft_json=draft_json,
                   at="scheduled_at",
                   status="scheduled",
                   time=scheduled_time
                )

    logger.info(f"Пользователь {message.from_user.id} — пост записан в БД со статусом scheduled на {scheduled_time}")
    await state.update_data(post_state="scheduled", post_id=post_id)
    await message.answer(
        f"✅ Пост запланирован на <b>{scheduled_time}</b>",
        reply_markup=cancel_or_back(),
        parse_mode="HTML"
    )

@publication_router.callback_query(F.data == CallbacksPublication.YES_ANSWER)
async def sync_post_yes_answer(callback: CallbackQuery, state: FSMContext):
    await state.update_data(scheduled_in_eny_case=True)
    await get_time_for_plan(message=callback.message, state=state)


@publication_router.callback_query(F.data == CallbacksPublication.CANCEL_POST_SCHEDULING)
async def question_about_cancel_scheduling_post(callback: CallbackQuery, state: FSMContext):
    await callback.message.edit_text("Вы уверены что хотите отменить планирование текущего поста?",
                                  reply_markup=y_or_n_for_cancel_post())


@publication_router.callback_query(F.data == CallbacksPublication.CANCEL_POST_SCHEDULING_YES_ANSWER)
async def cancel_scheduling_post(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    post_id = data.get("post_id")

    delete_status = await cancel_schedule_post(callback.from_user.id, post_id=post_id)
    if delete_status:
        await callback.answer("Удалено. Возврат...")
        await show_post(callback=callback, state=state)

    else:
        await callback.message.answer("Произошла ошибка при удалении поста из очереди на публикацию...\nПопробуйте в меню публикаций.",
                                      reply_markup=back_to())



@publication_router.callback_query(
        (F.data == CallbacksPublication.QUEUE_PUBLICATION) |
        (F.data.startswith(CallbacksPublication.CAROUSEL_POST_SCHEDULED_PREFIX)))
async def queue_posts(callback: CallbackQuery, state: FSMContext) -> None:
    user_id = callback.from_user.id
    if callback.data.startswith(CallbacksPublication.CAROUSEL_POST_SCHEDULED_PREFIX):
        current_page = int(callback.data.split("_")[-1])
        await state.update_data(current_page_schedule=current_page)

    else:
        data = await state.get_data()
        current_page = data.get("current_page")
        if not current_page:
            await state.update_data(current_page_schedule=1)
            current_page = 1

    logger.info(f"ID {user_id} открыл очередь публикаций, страница {current_page}")

    carousel_data = await get_carousel_data_from_db(user_id=user_id, current_page=current_page, status="scheduled") # -> CarouselResponse


    if carousel_data.post.post_id == 0 and carousel_data.post.status == "error":
        logger.info(f"Функция ---queue_posts--- пост для {user_id} не найден ")
        await callback.message.edit_text(
            text=TEXT_QUEUE_IS_NONE,
            reply_markup=create_buttons(
                texts=["✨ Создать пост","⬅️ Вернуться в меню публикаций"],
                callbacks=["create_post", "publication"]),
            parse_mode="HTML")
        return


    result = get_carousel_page_preview(data=carousel_data) # -> {"final_text": "", texts: [], callbacks: []}
    await callback.message.edit_text(result["final_text"],
                                     reply_markup=create_buttons(texts=result["texts"],
                                                                 callbacks=result["callbacks"],
                                                                 net=[3,1,1]),
                                     parse_mode="HTML")


@publication_router.callback_query(
    (F.data == CallbacksPublication.PUBLISHED_POST) |
    (F.data == CallbacksPublication.CAROUSEL_POST_PUBLISHED_PREFIX))
async def check_published_posts(callback: CallbackQuery, state: FSMContext):
    user_id = callback.from_user.id
    if callback.data.startswith(CallbacksPublication.CAROUSEL_POST_PUBLISHED_PREFIX):
        current_page = int(callback.data.split("_")[-1])
        await state.update_data(current_page_schedule=current_page)

    else:
        data = await state.get_data()
        current_page = data.get("current_page_published")
        if not current_page:
            await state.update_data(current_page_schedule=1)
            current_page = 1

    logger.info(f"ID {user_id} открыл очередь публикаций, страница {current_page}")
    carousel_data = await get_carousel_data_from_db(user_id=user_id,current_page=current_page, status="published")

    if carousel_data.post.post_id == 0 and carousel_data.post.status == "error":
        logger.info(f"Пост для {user_id} не найден ")
        await callback.message.edit_text(
            text=PUBLISHED_IS_NONE,
            reply_markup=create_buttons(
                texts=["✨ Создать пост","⬅️ Вернуться в меню публикаций"],
                callbacks=["create_post", "publication"]),
            parse_mode="HTML")
        return

    result = get_carousel_page_preview(data=carousel_data) # -> {"final_text": "", texts: [], callbacks: []}
    await callback.message.edit_text(result["final_text"],
                                     reply_markup=create_buttons(texts=result["texts"],
                                                                 callbacks=result["callbacks"],
                                                                 net=[3,1,1]),
                                     parse_mode="HTML")


@publication_router.callback_query(F.data == "-") # временное решение
async def remove_the_callback(callback: CallbackQuery): # временное решение
    pass # временное решение