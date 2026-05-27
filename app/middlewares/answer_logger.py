from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from AI_SMM_AGENT.app.config.settings import settings
from AI_SMM_AGENT.app.utils.logger import logging
from aiogram.dispatcher.event.handler import HandlerObject
from aiogram.exceptions import TelegramBadRequest

logger = logging.getLogger(__name__)


class CallbackAnswerLogger(BaseMiddleware):
    async def __call__(self, handler, event, data):

        by = "unknown, error"

        if isinstance(event, Message):
            if event.text and event.text.startswith("/"):
                by = "command"
            else:
                by = "message"

        elif isinstance(event, CallbackQuery):
            by = "button"

        state = data.get("state")
        if state:
            current_state = await state.get_state()
            if current_state:
                by = "state"

        current_handler: HandlerObject = data.get("handler")
        function_name = current_handler.callback.__name__ if current_handler else "Unknown handler"

        user_id = event.from_user.id if event.from_user else "Unknown user"

        logger.info(f"Пользователь ---{user_id}---, находиться в функции ---{function_name}---, попал в нее через ---{by}---")


        result = await handler(event, data)


        if isinstance(event, CallbackQuery):
            try:
                await event.answer()
            except TelegramBadRequest:
                pass

        return result
