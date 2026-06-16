# Стандартные библиотеки
import json
import logging
from datetime import datetime
from zoneinfo import ZoneInfo
from typing import Optional
from redis.asyncio import Redis

# Сторонние библиотеки
import pydantic
from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramAPIError

# Клавиатуры
from AI_SMM_AGENT.app.keyboards.general_inline import (
    draft_post, question_for_publication,
    pre_procedural_actions, publishing_post,
    clarifying_question, skip_question_or_back,
    edit_post_back_or_generate, retrying_request_and_back,
    manage_current_post, edit_post_back
)
from AI_SMM_AGENT.app.keyboards import back_to

# Модели и Состояния
from AI_SMM_AGENT.app.models.draft import MediaInput
from AI_SMM_AGENT.app.models.n8n import N8NStatus, N8NResult
from AI_SMM_AGENT.app.models.data_models import DraftPost, MediaType
from AI_SMM_AGENT.app.utils.states import CreatedPost
from AI_SMM_AGENT.app.models.n8n_exceptions import N8NError
from AI_SMM_AGENT.app.models.callbacks import CallbacksPost
from AI_SMM_AGENT.app.models.sessions_modes import SessionModes

# Сервисы и Репозитории
from AI_SMM_AGENT.app.services.draft import draft_working
from AI_SMM_AGENT.app.services.saved_style import get_style
from AI_SMM_AGENT.app.services.n8n_client import n8n_request
from AI_SMM_AGENT.app.services.post_service import sort_answer_n8n, get_telegram_file_url, publish_to_channel
from AI_SMM_AGENT.app.repositories.post_repo import db_created_post
from AI_SMM_AGENT.app.repositories.sessionID_repo import get_or_create_session
# from AI_SMM_AGENT.app.repositories.draft_repo import draft_saving
from AI_SMM_AGENT.app.services.working_with_post_status import process_n8n_response

# Middleware и Фильтры
from AI_SMM_AGENT.app.middlewares.albums_filters import AlbumMiddleware
from AI_SMM_AGENT.app.middlewares.exam_callback import ValidCallbackFilter

# Настройки
from AI_SMM_AGENT.app.config.settings import settings

# Помощники
from AI_SMM_AGENT.app.utils.cleanup_media import cleanup_media_messages

# UI Сервисы
from AI_SMM_AGENT.app.UI_Services.send_media_post import send_post_with_media

posts_router = Router()
posts_router.message.middleware(AlbumMiddleware())
posts_router.callback_query.filter(ValidCallbackFilter())

logger = logging.getLogger(__name__)


# ==================== ХЕНДЛЕРЫ ====================
@posts_router.callback_query(F.data == CallbacksPost.CREATE_POST)
async def cmd_create_post(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    text = (
        "<b>Создание публикации</b>\n\n"
        "Отправьте в чат исходные материалы для генерации. Система автоматически распознает формат и подготовит текст.\n\n"
        "<b>Поддерживаемые форматы:</b>\n"
        "» <b>Текст:</b> тезисы, сырые наброски или готовая тема\n"
        "» <b>Ссылки:</b> YouTube, Shorts, Reels, TikTok или посты из Telegram\n"
        "» <b>Аудио:</b> голосовые сообщения и файлы (транскрибация)\n"
        "» <b>Медиа:</b> изображения или видеоролики с описанием в подписи\n\n"
        "<b>Примеры запросов:</b>\n"
        "- <i>«Напиши экспертный пост про тренды SEO на основе этих тезисов...»</i>\n"
        "- <code>https://youtube.com...</code>\n\n"
        "<i>Пришлите файл, ссылку или текст для начала генерации...</i>"
    )

    await cleanup_media_messages(bot=bot, chat_id=callback.message.chat.id, state=state)
    await callback.message.edit_text(text=text, reply_markup=back_to(), parse_mode="HTML")
    await get_or_create_session(user_id=callback.from_user.id, mode=SessionModes.SET_SESSION_ID)
    await state.set_state(CreatedPost.WaitMessForPost)
    await state.update_data(edit_mode=False, draft_post=None)


@posts_router.message(CreatedPost.WaitMessForPost)
async def catch_all(message: Message, state: FSMContext, album: Optional[list[Message]] = None) -> None:
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

    quantity_photos, quantity_videos, draft_object = draft_working(media_items=media_items, object_of_draft=draft)
    await state.update_data(draft_post=draft_object.model_dump())

    markup = edit_post_back_or_generate() if edit_mode else draft_post()

    try:
        if album:
            await message.answer(
                text=f"<b>✅ Альбом добавлен в черновик</b>\n\n"
                     f"Успешно сохранено: фото — {quantity_photos}, видео — {quantity_videos}.\n\n"
                     f"Вы можете отправить дополнительные материалы или нажать кнопку ниже для запуска генерации 👇",
                reply_markup=markup,
                parse_mode="HTML"
            )
        else:
            await message.answer(
                text="<b>✅ Материал добавлен в черновик</b>\n\n"
                     "Ваше сообщение успешно сохранено. Вы можете отправить вдогонку дополнительные материалы "
                     "(например, текст-пояснение или фотографии).\n\n"
                     "Если все готово — нажмите кнопку ниже для запуска генерации 👇",
                reply_markup=markup,
                parse_mode="HTML"
            )
    except TelegramAPIError as e:
        logger.error(f"Ошибка отправки подтверждения черновика: {e}")


@posts_router.callback_query(F.data.in_([
    CallbacksPost.GENERATE_POST,
    CallbacksPost.GENERATION_IN_ENY_CASE,
    CallbacksPost.RETRY_REQUEST_TO_N8N
]))
async def send_request_for_post(callback: CallbackQuery, state: FSMContext, redis_client: Redis) -> Message | None:
    is_retry = callback.data == CallbacksPost.RETRY_REQUEST_TO_N8N
    message = await callback.message.edit_text("⏳ Повторяю запрос..." if is_retry else "⏳ Отправляю запрос...") # ✨

    data = await state.get_data()
    draft_dict = data.get("draft_post")
    logger.debug(draft_dict)
    if not draft_dict:
        await callback.answer("Не актуально")
        return None

    user_id = callback.from_user.id
    forcing_to_generate = callback.data == CallbacksPost.GENERATION_IN_ENY_CASE

    user_session_id = await get_or_create_session(user_id=user_id, mode=SessionModes.GET_SESSION_ID)
    style = await get_style(user_id)

    if not user_session_id:
        return await message.answer("Произошла ошибка управлением памятью контекста ИИ-агента, попробуйте заново...",
                                    reply_markup=back_to())

    payload = {
        "action": "GENERATE_POST",
        "user_id": user_id,
        "session_id": user_session_id,
        "chat_id": callback.message.chat.id,
        "draft": draft_dict,
        "brand_settings": style,
        "publication_status": forcing_to_generate
    }

    logger.info(f"Sending payload for {user_id} | publication_status={forcing_to_generate} | brand={style}")

    # try:
    #     response = await n8n_request.send_payload(payload)
    # except N8NError as e:
    #     logger.error(f"N8N недоступен: {e}")
    #     return await message.edit_text("Ошибка, к сожалению сервис недоступен...", reply_markup=retrying_request_and_back())
    #
    # if response is None:
    #     logger.error("Нет ответа от N8N")
    #     return await message.edit_text("Ошибка, к сожалению сервис недоступен...", reply_markup=retrying_request_and_back())

    # logger.info(f"N8N response: {response}")
    # result = sort_answer_n8n(response)

    success, result, markup = await process_n8n_response(payload, draft_dict)  # тут SUCCESS не возвращается поэтому без проверок

    if isinstance(result, N8NResult):
        final_text = result.final_text

        await state.update_data(current_media=result.media_assessment)
        logger.info(f"Selected file_ids from N8N: {result.selected_file_ids}")

    else:
        final_text = result
        markup = retrying_request_and_back()

    mssg_id = await message.edit_text(text=final_text, reply_markup=markup, parse_mode="HTML")

    logger.info(f"Draft media file_ids: {[m['file_id'] for m in draft_dict.get('media', [])]}")

    await redis_client.set(f"generation_msg:{message.chat.id}", mssg_id.message_id, ex=600)
    logger.info(f"---send_request_for_post--- message_id для {user_id}сохранен в redis")

# @posts_router.callback_query(F.data == CallbacksPost.DRAFT_SAVE)
# async def draft_save(callback: CallbackQuery, state: FSMContext):
#     await draft_saving()



@posts_router.callback_query(F.data == CallbacksPost.SHOW_POST)
async def show_post(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    post = data.get("generated_text")
    draft_dict = data.get("draft_post")
    media_sent = data.get("media_sent")

    if not post:
        return await callback.message.edit_text(
            "Произошла ошибка, вернитесь в меню и попробуйте заново",
            reply_markup=back_to()
        )

    draft = DraftPost.model_validate(draft_dict) if draft_dict else None
    photos = _get_photos_from_draft(draft, draft_dict) if draft else []

    logger.info(f"show_post: selected_ids={draft.selected_media_ids if draft else []}, photos count={len(photos)}")

    logger.info(f"show_post: media_sent={media_sent}")
    sent_message = await send_post_with_media(
        callback=callback,
        text=post,
        photos=photos,
        markup=pre_procedural_actions(),
        media_already_sent=media_sent
    )
    if not media_sent:
        await state.update_data(sent_message=sent_message, media_sent=True)


@posts_router.callback_query(F.data == CallbacksPost.QUESTION_FOR_POST)
async def cmd_question_for_publication(callback: CallbackQuery, state: FSMContext, bot: Bot):
    data = await state.get_data()
    if not data.get("post_state"):
        return await callback.answer("Не актуально")

    # await state.update_data(media_sent=False)
    # await cleanup_media_messages(bot=bot, chat_id=callback.message.chat.id, state=state)

    await callback.message.edit_text(
        text=data.get("generated_text"),
        reply_markup=question_for_publication(),
        parse_mode="HTML"
    )


@posts_router.callback_query(F.data == CallbacksPost.PUBLISHING_POST)
async def cmd_publishing_post(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if not data.get("post_state"):
        return await callback.answer("Не актуально")

    generated_text = data.get("generated_text")
    moscow_time = datetime.now(ZoneInfo("Europe/Moscow"))

    try:
        if generated_text is None:
            logger.critical("Пост утерян в cmd_publishing_post — generated_text = None")
            await callback.message.answer("Произошла ошибка, пост не сохранён. Попробуйте снова.",
                                          reply_markup=publishing_post())
            return

        draft = DraftPost.model_validate(data.get("draft_post"))
        post_record = json.dumps({
            "text": generated_text,
            "selected_media_ids": draft.selected_media_ids
        }, ensure_ascii=False)

        await db_created_post(
            user_id=callback.from_user.id,
            draft_json=post_record,
            at="published_at",
            status="published",
            time=moscow_time.strftime("%Y-%m-%d %H:%M:%S")
        )

    except Exception as e:
        logger.critical(f"Пост не сохранён в БД: {e}", exc_info=True)
        await callback.message.edit_text("Произошла ошибка, пост не сохранён. Попробуйте снова.",
                                         reply_markup=publishing_post())
        return

    await state.update_data(post_state="published")
    await publish_to_channel(
        bot=callback.bot,
        channel_id=settings.CHANNEL_ID,
        text=generated_text,
        draft_object=data.get("draft_post")
    )
    await callback.message.edit_text(text="<b>Пост был успешно опубликован</b>",
                                     reply_markup=manage_current_post(),
                                     parse_mode="HTML")


@posts_router.callback_query(F.data == CallbacksPost.EDIT_CURRENT_POST)
async def edit_current_post(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    if not data.get("post_state"):
        return await callback.answer("Не актуально")

    post_text = data.get("generated_text")
    user_mssg = await callback.message.edit_text(
        f"{post_text}\n\n\n\n<b>Что поменять в вашем посте? Напишите прямо в чат.</b>",
        reply_markup=edit_post_back(),
        parse_mode="HTML"
    )

    await state.update_data(message_id=user_mssg.message_id)
    await state.set_state(CreatedPost.WaitMessForPost)
    await state.update_data(edit_mode=True)


@posts_router.callback_query(F.data == CallbacksPost.APPLY_EDIT)
async def apply_edit(callback: CallbackQuery, state: FSMContext):
    data = await state.get_data()
    draft = data.get("draft_post")
    original_post = data.get("generated_text")
    user_id = callback.from_user.id

    session_id = await get_or_create_session(user_id=user_id, mode=SessionModes.GET_SESSION_ID)
    if not session_id:
        return await callback.message.answer("Произошла ошибка управлением памятью контекста ИИ-агента, попробуйте заново...",
                                             reply_markup=back_to())

    payload = {
        "action": "EDIT_POST",
        "user_id": user_id,
        "session_id": session_id,
        "chat_id": callback.message.chat.id,
        "original_post": original_post,
        "what_edit": draft
    }

    try:
        response = await n8n_request.send_payload(payload)
    except N8NError as e:
        logger.error(f"N8N недоступен: {e}")
        return await callback.message.edit_text("Ошибка, к сожалению сервис недоступен...",
                                                reply_markup=retrying_request_and_back())

    if response is None:
        logger.error("Нет ответа от N8N")
        return await callback.message.edit_text("Ошибка, к сожалению сервис недоступен...",
                                                reply_markup=retrying_request_and_back())

    logger.info(f"N8N response: {response}")
    result = sort_answer_n8n(response)

    markup = back_to()
    if result.status == N8NStatus.SUCCESS:
        markup = pre_procedural_actions()
        await state.update_data(generated_text=result.post_text, post_state="generated")

    elif result.status == N8NStatus.REJECTION:
        markup = clarifying_question()

    elif result.status == N8NStatus.QUESTION:
        markup = skip_question_or_back()
        await state.update_data(generated_text=result.final_text, original_payload=payload)

    await callback.message.answer(text=result.final_text, reply_markup=markup, parse_mode="HTML")


@posts_router.message(CreatedPost.AnswerOnQuestionAi)
async def answer_on_question_about_post(message: Message, state: FSMContext):
    logger.error("DEBUG: пользователь в answer_on_question_about_post")  # убрать после отладки
    data = await state.get_data()
    original_post = data.get("generated_text")
    bot_mssg_id = data.get("message_id")
    user_id = message.from_user.id

    user_session_id = await get_or_create_session(user_id=user_id, mode=SessionModes.GET_SESSION_ID)
    if not user_session_id:
        return await message.answer("Произошла ошибка управлением памятью контекста ИИ-агента, попробуйте заново...",
                                    reply_markup=back_to())

    payload = {
        "action": "CORRECTING_CURRENT_POST",
        "user_id": user_id,
        "session_id": user_session_id,
        "chat_id": message.chat.id,
        "original_post": original_post,
        "what_correcting": message.text
    }

    try:
        response = await n8n_request.send_payload(payload)
    except N8NError as e:
        logger.error(f"N8N недоступен: {e}")
        return await message.bot.edit_message_text(chat_id=message.chat.id,
                                                   message_id=bot_mssg_id,
                                                   text="Ошибка, к сожалению сервис недоступен...",
                                                   reply_markup=retrying_request_and_back())

    if response is None:
        logger.error("Нет ответа от N8N")
        return await message.bot.edit_message_text(chat_id=message.chat.id,
                                                   message_id=bot_mssg_id,
                                                   text="Ошибка, к сожалению сервис недоступен...",
                                                   reply_markup=retrying_request_and_back())

    logger.info(f"N8N response: {response}")
    result = sort_answer_n8n(response)

    # if result.status == N8NStatus.SUCCESS:
    #     markup = pre_procedural_actions()
    # elif result.status == N8NStatus.REJECTION:         - т.к это не конечный ответ (соответственно кнопки не нужны)
    #     markup = clarifying_question()
    # elif result.status == N8NStatus.QUESTION:
    #     markup = skip_question_or_back()
    # else:
    #     markup = back_to()

    await message.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=bot_mssg_id,
        text=result.final_text,
        # reply_markup=markup,- т.к это не конечный ответ (соответственно кнопки не нужны)
        parse_mode="HTML"
    )