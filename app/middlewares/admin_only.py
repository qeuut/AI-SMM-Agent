from typing import Any, Awaitable, Callable, Dict
from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from AI_SMM_AGENT.app.config.settings import settings
from AI_SMM_AGENT.app.utils.logger import logger

class AdminOnlyMiddleware(BaseMiddleware):
    async def __call__(
        self,
        handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
        event: Message | CallbackQuery,
        data: Dict[str, Any],
    ) -> Any:
        user_id = event.from_user.id
        if user_id not in settings.admin_ids:
            logger.warning(f"Access denied for user {user_id}")
            return
        return await handler(event, data)