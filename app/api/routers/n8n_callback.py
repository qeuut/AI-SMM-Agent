# from AI_SMM_AGENT.app.services.post_service import sort_answer_n8n
# from AI_SMM_AGENT.app.services.working_with_post_status import process_n8n_response
# from AI_SMM_AGENT.app.models.n8n import N8NStatus

import logging
from fastapi import APIRouter
from pydantic import BaseModel
from aiogram import Bot, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.exceptions import TelegramAPIError
from redis.asyncio import Redis


from AI_SMM_AGENT.app.models.n8n import N8NStatus
from AI_SMM_AGENT.app.services.working_with_post_status import process_n8n_status
from AI_SMM_AGENT.app.UI_Services.send_media_post import send_post_with_media
from AI_SMM_AGENT.app.keyboards.general_inline import pre_procedural_actions


logger = logging.getLogger(__name__)


class N8NCallbackPayload(BaseModel):
    media_for_publish: list
    chat_id: int
    status_generate: str
    post: str | None = None


def get_n8n_router(bot: Bot, redis: Redis, dp: Dispatcher) -> APIRouter:
    router = APIRouter(prefix="/n8n", tags=["n8n"])

    @router.post("/callback")
    async def n8n_callback(payload: N8NCallbackPayload):
        try:
            storage_key = StorageKey(
                bot_id=bot.id,
                chat_id=payload.chat_id,
                user_id=payload.chat_id
            )

            state: FSMContext = FSMContext(
                storage=dp.storage,
                key=storage_key
            )

            state_data = await state.get_data()
            draft_dict = state_data.get("draft_post", {})

            result, reply_markup = await process_n8n_status(
                n8n_response=payload.model_dump(),
                draft_dict=draft_dict
            )

            text_to_send = None

            logger.info(f"Получен статус от N8N: {result.status}")

            if result.status == N8NStatus.SUCCESS:
                text_to_send = result.final_text
                # Обновляем FSM: сохраняем сгенерированный текст и меняем шаг
                await state.update_data(post_state="generated", generated_text=result.post_text)
                logger.info(f"FSM обновлен для {payload.chat_id}: пост сгенерирован")

            elif result.status == N8NStatus.REJECTION:
                text_to_send = result.reason_reject_text
                await state.set_state("waiting_for_user_clarification")

            elif result.status == N8NStatus.QUESTION:
                text_to_send = result.question_text
                await state.set_state("waiting_for_user_clarification")

            else:
                text_to_send = result.final_text or "Обработка запроса завершена."

            if not text_to_send:
                text_to_send = "Получен пустой ответ от системы ИИ."

            message_id = None
            key = f"generation_msg:{payload.chat_id}"
            cached_msg_id = await redis.get(key)

            logger.debug(f"ищу ключ '{key}' | Получено значение: {cached_msg_id}")

            if cached_msg_id:
                message_id = int(cached_msg_id)
                await redis.delete(key)  # очистка кэша
            else:
                logger.warning(f"ID загрузочного сообщения не найден в Redis для чата {payload.chat_id}")

            if payload.media_for_publish is not None: # н8н всегда возвращает список
                await send_post_with_media(
                    bot=bot,
                    text=payload.post,
                    photos=payload.media_for_publish,
                    markup=pre_procedural_actions()
                )

            if message_id:
                try:
                    await bot.edit_message_text(
                        chat_id=payload.chat_id,
                        message_id=message_id,
                        text=text_to_send,
                        parse_mode="HTML",
                        reply_markup=reply_markup
                    )
                    logger.info("Сообщение успешно отредактировано в n8n_callback")
                except TelegramAPIError as e:
                    logger.warning(f"Не удалось отредактировать сообщение: {e}. Отправляем новое.")
                    await bot.send_message(
                        chat_id=payload.chat_id,
                        text=text_to_send,
                        parse_mode="HTML",
                        reply_markup=reply_markup
                    )
            else:
                await bot.send_message(
                    chat_id=payload.chat_id,
                    text=text_to_send,
                    parse_mode="HTML",
                    reply_markup=reply_markup
                )
                logger.info("Отправлено новое сообщение (ID не найден в Redis)")

            logger.info(
                f"Финальные кнопки: {reply_markup.__class__.__name__ if reply_markup else 'Отсутствуют (None)'}")

            return {"ok": True}

        except TelegramAPIError as e:
            logger.error(f"Telegram error в n8n_callback: {e}")
            return {"ok": False, "error": f"Telegram error: {e}"}
        except Exception as e:
            logger.error(f"Ошибка в n8n_callback: {e}")
            return {"ok": False, "error": str(e)}

    return router
