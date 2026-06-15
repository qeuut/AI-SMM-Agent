from fastapi import APIRouter
from pydantic import BaseModel
from aiogram import Bot
from aiogram.exceptions import TelegramAPIError

from AI_SMM_AGENT.app.services.post_service import sort_answer_n8n


# 1. Исправляем модель: добавляем chat_id и делаем post необязательным (на случай вопросов от ИИ)
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
                return {
                    "ok": False,
                    "error": "Failed to process n8n payload"
                }

            # 2. Достаем асинхронный клиент Redis, который вы сохранили в bot.redis внутри main.py
            redis_client = getattr(bot, "redis", None)
            message_id = None

            if redis_client:
                key = f"generation_msg:{payload.chat_id}"
                cached_msg_id = await redis_client.get(key)
                if cached_msg_id:
                    message_id = int(cached_msg_id)
                    await redis_client.delete(key)  # Чистим кэш после успешного получения

            # 3. Если нашли ID в Redis — плавно редактируем старую плашку, иначе — отправляем новую
            if message_id:
                try:
                    await bot.edit_message_text(
                        chat_id=payload.chat_id,
                        message_id=message_id,
                        text=n8n_object.final_text,
                        parse_mode="HTML",
                    )
                except TelegramAPIError:
                    # Страховка на случай, если сообщение было удалено пользователем
                    await bot.send_message(
                        chat_id=payload.chat_id,
                        text=n8n_object.final_text,
                        parse_mode="HTML",
                    )
            else:
                # Страховка, если кэш в Redis отсутствует или истек
                await bot.send_message(
                    chat_id=payload.chat_id,
                    text=n8n_object.final_text,
                    parse_mode="HTML",
                )

            return {"ok": True}

        except TelegramAPIError as e:
            return {
                "ok": False,
                "error": f"Telegram error: {e}"
            }

        except Exception as e:
            return {
                "ok": False,
                "error": str(e)
            }

    return router
