import sys
import app as AI_SMM_AGENT
sys.modules["AI_SMM_AGENT"] = AI_SMM_AGENT


from fastapi import FastAPI
import uvicorn

from aiogram import Bot
from AI_SMM_AGENT.app.api.routers.n8n_callback import get_n8n_router


def create_app(bot: Bot) -> FastAPI:
    app = FastAPI()
    app.include_router(get_n8n_router(bot))
    return app


async def run_api_server(bot: Bot, host: str = "0.0.0.0", port: int = 8080):
    app = create_app(bot)
    config = uvicorn.Config(app, host=host, port=port, log_level="info")
    server = uvicorn.Server(config)
    await server.serve()