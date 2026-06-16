import logging
from fastapi import APIRouter
from pydantic import BaseModel
from aiogram import Bot, Dispatcher
from aiogram.fsm.context import FSMContext
from aiogram.fsm.storage.base import StorageKey
from aiogram.exceptions import TelegramAPIError
from redis.asyncio import Redis

from AI_SMM_AGENT.app.services.post_service import sort_answer_n8n
from AI_SMM_AGENT.app.services.working_with_post_status import process_n8n_response
from AI_SMM_AGENT.app.models.n8n import N8NStatus

logger = logging.getLogger(__name__)


class N8NCallbackPayload(BaseModel):
    chat_id: int
    status_generate: str
    post: str | None = None


def get_n8n_router(bot: Bot, redis: Redis, dp: Dispatcher) -> APIRouter:
    router = APIRouter(prefix="/n8n", tags=["n8n"])

    @router.post("/callback")
    async def n8n_callback(payload: N8NCallbackPayload):
        try:
            # 1. Получаем доступ к FSM-контексту пользователя в Redis
            storage_key = StorageKey(
                bot_id=bot.id,
                chat_id=payload.chat_id,
                user_id=payload.chat_id
            )
            state: FSMContext = dp.fsm.resolve_context(bot, storage_key)

            # Извлекаем текущий черновик поста для передачи в оркестратор
            state_data = await state.get_data()
            draft_dict = state_data.get("draft_post", {})

            # 2. Вызываем оркестратор (он внутри делает сеть и обновляет черновик)
            # Возвращает: (success, result_данные_или_ошибка, markup_или_кнопка)
            success, result, markup = await process_n8n_response(
                payload=payload.model_dump(),
                draft_dict=draft_dict
            )

            # Переменные для отправки в Telegram
            text_to_send = None
            reply_markup = None

            if success:

                # В случае успеха result — это готовый датакласс N8NResult (из функции sort_answer_n8n)
                reply_markup = markup  # Берем сгенерированную клавиатуру
                logger.info(f"Кнопки: {reply_markup.__class__.__name__ if reply_markup else 'Отсутствуют (None)'}")
                # Распределяем логику и тексты на основе статуса из датакласса
                if result.status == N8NStatus.SUCCESS:
                    text_to_send = result.final_text
                    # Обновляем FSM: сохраняем сгенерированный текст и меняем шаг
                    await state.update_data(post_state="generated", generated_text=result.post_text)
                    logger.info(f"FSM обновлен для {payload.chat_id}: пост сгенерирован")

                elif result.status == N8NStatus.REJECTION:
                    text_to_send = result.reason_reject_text
                    # Переводим пользователя в режим ожидания нового ввода/уточнения
                    await state.set_state("waiting_for_user_clarification")

                elif result.status == N8NStatus.QUESTION:
                    text_to_send = result.question_text
                    await state.set_state("waiting_for_user_clarification")

                else:
                    # Для остальных статусов (error, unknown, connected)
                    text_to_send = result.final_text or "Обработка запроса завершена."
            else:
                # Если оркестратор вернул ошибку сети/сервиса (success == False)
                # result — это строка "Ошибка, к сожалению сервис недоступен..."
                text_to_send = result
                # markup — это булевый флаг buttons_status (True)
                if markup:
                    from AI_SMM_AGENT.app.keyboards.general_inline import retrying_request_and_back
                    reply_markup = retrying_request_and_back()

            if not text_to_send:
                text_to_send = "Получен пустой ответ от системы ИИ."

            # 3. Логика работы с кэшем загрузочного сообщения в Redis
            message_id = None
            key = f"generation_msg:{payload.chat_id}"
            cached_msg_id = await redis.get(key)

            logger.debug(f"ищу ключ '{key}' | Получено значение: {cached_msg_id}")

            if cached_msg_id:
                message_id = int(cached_msg_id)
                await redis.delete(key)  # Чистим кэш
            else:
                logger.warning(f"ID загрузочного сообщения не найден в Redis для чата {payload.chat_id}")

            # 4. Отправка результата пользователю (Редактирование или Новое сообщение)
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

            return {"ok": True}

        except TelegramAPIError as e:
            logger.error(f"Telegram error в n8n_callback: {e}")
            return {"ok": False, "error": f"Telegram error: {e}"}
        except Exception as e:
            logger.error(f"Критическая ошибка в n8n_callback: {e}")
            return {"ok": False, "error": str(e)}

    return router
