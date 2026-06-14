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
        # если не альбом - пропускаем
        if not event.media_group_id:
            return await handler(event, data)

        mg_id = str(event.media_group_id)

        if mg_id not in self.cache:
            self.cache[mg_id] = []
        self.cache[mg_id].append(event)

        # ждем остальных частей альбома
        await asyncio.sleep(self.latency)

        if event != self.cache.get(mg_id, [])[-1]:
            return

        # добавляем все что наловили в основной список с медиа
        data["album"] = self.cache.pop(mg_id)
        return await handler(event, data)