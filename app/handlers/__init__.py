from aiogram import Router
from AI_SMM_AGENT.app.handlers.content_plan import content_plan_router
from AI_SMM_AGENT.app.handlers.navigation import navigation_router
from AI_SMM_AGENT.app.handlers.posts import posts_router
from AI_SMM_AGENT.app.handlers.publication import publication_router
from AI_SMM_AGENT.app.handlers.settings import settings_router
from AI_SMM_AGENT.app.handlers.statistic import statistic_router
from AI_SMM_AGENT.app.handlers.style import style_router


main_router = Router()
main_router.include_router(content_plan_router)
main_router.include_router(navigation_router)
main_router.include_router(posts_router)
main_router.include_router(publication_router)
main_router.include_router(settings_router)
main_router.include_router(statistic_router)
main_router.include_router(style_router)