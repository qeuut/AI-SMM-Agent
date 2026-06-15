import logging

from fastapi import APIRouter
from pydantic import BaseModel
from aiogram import Bot
from aiogram.exceptions import TelegramAPIError

from AI_SMM_AGENT.app.services.post_service import sort_answer_n8n

logger = logging.getLogger(__name__)


class N8NCallbackPayload(BaseModel):
    chat_id: int
    status_generate: str
    post: str | None = None


def get_n8n_router(bot: Bot) -> APIRouter:
    router = APIRouter(prefix="/n8n", tags=["n8n"])

    @router.post("/callback")
    async def n8n_callback(payload: N8NCallbackPayload):
        try:
            n8n_object = sort_answer_n8n(payload.model_dump())

            if not n8n_object:
                logger.error("Функция ---n8n_callback--- Не удалось обработать payload")
                return {
                    "ok": False,
                    "error": "Failed to process n8n payload"
                }

            redis_client = getattr(bot, "redis", None)
            message_id = None

            if redis_client:
                key = f"generation_msg:{payload.chat_id}"
                cached_msg_id = await redis_client.get(key)

                # Добавляем лог для отладки кэша
                logger.debug("ищу ключ '{key}' | Получено значение: {cached_msg_id} (тип: {type(cached_msg_id)})")

                if cached_msg_id:
                    message_id = int(cached_msg_id)
                    await redis_client.delete(key)  # очистка кэша после успешного получения
            else:
                logger.warning("WARNING: redis_client не найден в объекте bot!")

            # eсли id найден в redis
            if message_id:
                try:
                    await bot.edit_message_text(
                        chat_id=payload.chat_id,
                        message_id=message_id,
                        text=n8n_object.final_text,
                        parse_mode="HTML",
                    )
                    logger.info("Функция ---n8n_callback--- сообщение было обновлено")
                except TelegramAPIError as e:
                    # eсли сообщение было удалено пользователем или слишком старое
                    logger.warning(f"Не удалось отредактировать сообщение: {e}. Отправляем новое.")
                    await bot.send_message(
                        chat_id=payload.chat_id,
                        text=n8n_object.final_text,
                        parse_mode="HTML",
                    )
                    logger.info("Функция ---n8n_callback--- сообщение не было обновлено (отправлено новое)")
            else:
                # если кэш в redis отсутствует или истек по ttl
                await bot.send_message(
                    chat_id=payload.chat_id,
                    text=n8n_object.final_text,
                    parse_mode="HTML",
                )
                logger.info("Функция ---n8n_callback--- сообщение было отправлено (ID не найден в Redis)")

            return {"ok": True}

        except TelegramAPIError as e:
            logger.error(f"Telegram error в n8n_callback: {e}")
            return {
                "ok": False,
                "error": f"Telegram error: {e}"
            }

        except Exception as e:
            logger.error(f"Критическая ошибка в n8n_callback: {e}")
            return {
                "ok": False,
                "error": str(e)
            }

    return router
