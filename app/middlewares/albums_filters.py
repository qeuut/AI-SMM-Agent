import asyncio
from typing import Any, Awaitable, Callable, Dict, List
from aiogram import BaseMiddleware
from aiogram.types import Message


class AlbumMiddleware(BaseMiddleware):
    def __init__(self, latency: float = 0.1):
        self.latency = latency
        self.cache: Dict[str, List[Message]] = {}

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        # Если это не альбом идем дальше
        if not event.media_group_id:
            return await handler(event, data)

        mg_id = str(event.media_group_id)

        if mg_id not in self.cache:
            self.cache[mg_id] = []
        self.cache[mg_id].append(event)

        # Ждем пока прилетят остальные части
        await asyncio.sleep(self.latency)

        if event != self.cache.get(mg_id, [])[-1]:
            return

        # Добавляем весь список сообщений в данные для handler
        data["album"] = self.cache.pop(mg_id)
        return await handler(event, data)
