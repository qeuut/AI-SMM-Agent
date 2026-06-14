from fastapi import APIRouter
from aiogram import Bot

from app.services.post_service import sort_answer_n8n


router = APIRouter(prefix="/n8n", tags=["n8n"])


def get_n8n_router(bot: Bot) -> APIRouter:
    @router.post("/callback")
    async def n8n_callback(payload: dict):
        chat_id = payload.get("chat_id")
        n8n_object = sort_answer_n8n(payload)
        await bot.send_message(
            chat_id=chat_id,
            text=n8n_object.final_text,
            parse_mode="HTML"
        )
        return {"ok": True}

    return router