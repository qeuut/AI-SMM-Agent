import aiohttp
import logging
import asyncio

from AI_SMM_AGENT.app.config.settings import settings
from AI_SMM_AGENT.app.models.n8n_exceptions import N8NConnectionError, N8NResponseError


logger = logging.getLogger(__name__)


class N8NClient:
    def __init__(self, webhook_url: str) -> None:
        self.webhook_url = webhook_url

    async def send_payload(self, payload: dict) -> any:
        try:

            timeout = aiohttp.ClientTimeout(total=30) # если н8н отвалиться и перестанет отвечать
            async with aiohttp.ClientSession(timeout=timeout) as session: # если н8н отвалиться и перестанет отвечать
                async with session.post(self.webhook_url, json=payload) as resp:
                    if resp.status != 200:
                        raise N8NResponseError(f"N8N :: статус {resp.status}")
                    return await resp.json()

        except aiohttp.ClientConnectionError as e:
            logger.error("Н8Н :: не удалось соединиться")
            raise N8NConnectionError from e

        except aiohttp.ContentTypeError as e:
            logger.error("Н8Н :: ошибка ответа")
            raise N8NResponseError() from e

        except asyncio.TimeoutError as e:
            logger.error("Н8Н :: превышено время ожидание")
            raise N8NConnectionError("timeout") from e

n8n_request = N8NClient(webhook_url=settings.N8N_WEBHOOK_URL)