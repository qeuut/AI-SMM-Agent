import asyncio

from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import Redis

# from AI_SMM_AGENT.app.api.server import run_api_server
from AI_SMM_AGENT.app.api.server import run_api_server # для railway
from AI_SMM_AGENT.app.config.settings import settings
from AI_SMM_AGENT.app.handlers import main_router as main_router
from AI_SMM_AGENT.app.middlewares.admin_only import AdminOnlyMiddleware
from AI_SMM_AGENT.app.utils.logger import logger
from AI_SMM_AGENT.app.middlewares.answer_logger import CallbackAnswerLogger
from AI_SMM_AGENT.app.services.database import connect_db, init_db, disconnect_db
from AI_SMM_AGENT.app.services.scheduler import run_scheduler


async def on_startup(bot: Bot):
    await connect_db()
    await init_db()
    asyncio.create_task(run_scheduler(bot))

async def on_shutdown():
    await disconnect_db()


async def main():
    logger.info("Starting bot...")

    redis = Redis.from_url(settings.REDIS_URL, decode_responses=True)
    storage = RedisStorage(redis=redis)

    bot = Bot(token=settings.BOT_TOKEN)
    dp = Dispatcher(storage=storage)

    dp.workflow_data["bot"] = bot

    # middlewares
    dp.message.middleware(AdminOnlyMiddleware())
    dp.callback_query.middleware(AdminOnlyMiddleware())
    dp.message.middleware(CallbackAnswerLogger())
    dp.callback_query.middleware(CallbackAnswerLogger())

    dp.include_router(main_router)

    # хуки для соединения с бд
    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)


    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Bot started polling")
    await asyncio.gather(
        dp.start_polling(bot, redis_client=redis),
        run_api_server(bot, redis, dp)
    )


if __name__ == "__main__":
    asyncio.run(main())