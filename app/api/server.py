from redis.asyncio import Redis
from fastapi import FastAPI
import uvicorn

from aiogram import Bot, Dispatcher
from AI_SMM_AGENT.app.api.routers.n8n_callback import get_n8n_router


def create_app(bot: Bot, redis: Redis, dp: Dispatcher) -> FastAPI:
    app = FastAPI()
    app.include_router(get_n8n_router(bot, redis, dp))
    return app


async def run_api_server(bot: Bot, redis: Redis, dp: Dispatcher, host: str = "0.0.0.0", port: int = 8080):
    app = create_app(bot, redis, dp)
    config = uvicorn.Config(app, host=host, port=port, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()