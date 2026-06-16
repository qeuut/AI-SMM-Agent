import logging
from fastapi import APIRouter
from pydantic import BaseModel
from aiogram import Bot, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.exceptions import TelegramAPIError
from redis.asyncio import Redis

from AI_SMM_AGENT.app.services.working_with_post_status import process_n8n_response

logger = logging.getLogger(__name__)


class N8NCallbackPayload(BaseModel):
    chat_id: int
    status_generate: str
    post: str | None = None


def get_n8n_router(bot: Bot, redis: Redis, dp: Dispatcher) -> APIRouter:  # 1. Принимаем dp
    router = APIRouter(prefix="/n8n", tags=["n8n"])

    @router.post("/callback")
    async def n8n_callback(payload: N8NCallbackPayload):
        try:
            # 2. Подключаемся к FSM конкретного пользователя в Redis
            storage_key = StorageKey(
                bot_id=bot.id,
                chat_id=payload.chat_id,
                user_id=payload.chat_id
            )
            state: FSMContext = dp.fsm.resolve_context(bot, storage_key)

            # Извлекаем текущие данные FSM (нам нужен черновик)
            state_data = await state.get_data()
            draft_dict = state_data.get("draft_post", {})

            # 3. Запускаем ваш оркестратор (передаем payload-словарь и черновик)
            # Измените в вызове payload= на payload.model_dump()
            success, data, markup_or_button = await process_n8n_response(
                payload=payload.model_dump(),
                draft_dict=draft_dict
            )

            # Определяем текст для отправки
            if success:
                # data — это датакласс N8NResult. Берём final_text или тексты вопросов
                text_to_send = data.final_text or data.question_text or data.reason_reject_text
                reply_markup = markup_or_button

                # 4. Обновляем FSM состояние в зависимости от статуса ответа ИИ
                from AI_SMM_AGENT.app.models.n8n import N8NStatus
                if data.status == N8NStatus.SUCCESS:
                    await state.update_data(post_state="generated", generated_text=data.post_text)
                else:
                    # Если это вопрос или отказ — ставим стейт ожидания ответа пользователя
                    await state.set_state("waiting_for_user_clarification")
            else:
                # data — это строка с ошибкой "Ошибка, сервис недоступен..."
                text_to_send = data
                # Подставляем кнопку повтора, если флаг markup_or_button == True
                from AI_SMM_AGENT.app.keyboards.general_inline import retrying_request_and_back
                reply_markup = retrying_request_and_back() if markup_or_button else None

            if not text_to_send:
                text_to_send = "Получен пустой ответ от ИИ-агента."

            # 5. Логика работы с кэшем сообщений Telegram (без изменений)
            message_id = None
            key = f"generation_msg:{payload.chat_id}"
            cached_msg_id = await redis.get(key)

            logger.debug(f"ищу ключ '{key}' | Получено значение: {cached_msg_id}")

            if cached_msg_id:
                message_id = int(cached_msg_id)
                await redis.delete(key)
            else:
                logger.warning("Функция ---n8n_callback--- id сообщения не найден в Redis кэше")

            # Отправка/Редактирование
            if message_id:
                try:
                    # Пытаемся отредактировать старое «загрузочное» сообщение
                    await bot.edit_message_text(
                        chat_id=payload.chat_id,
                        message_id=message_id,
                        text=text_to_send,
                        parse_mode="HTML",
                        reply_markup=reply_markup
                    )
                    logger.info("Функция ---n8n_callback--- сообщение было обновлено")
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
                logger.info("Функция ---n8n_callback--- отправлено новое сообщение")

            return {"ok": True}

        except TelegramAPIError as e:
            logger.error(f"Функция ---n8n_callback--- Telegram error: {e}")
            return {"ok": False, "error": f"Telegram error: {e}"}
        except Exception as e:
            logger.error(f"Функция ---n8n_callback--- критическая ошибка: {e}")
            return {"ok": False, "error": str(e)}

    return router
