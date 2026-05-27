# Стандартные библиотеки
import logging

# Сторонние библиотеки
from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

# Клавиатуры
from AI_SMM_AGENT.app.keyboards.general_inline import (
    main_menu
)

# модели
from AI_SMM_AGENT.app.models.callbacks import CallbacksNavigation, CallbacksStyle

# репозитории, сервисы
from AI_SMM_AGENT.app.repositories.post_repo import get_or_create_session

# модели
...

# Помощники
from AI_SMM_AGENT.app.utils.cleanup_media import cleanup_media_messages


navigation_router = Router()


logger = logging.getLogger(__name__)


async def cmd_start(message: Message, edit: bool = False) -> Message | None:
    text = (
        "<b>👋 Приветствую! Я ваш персональный AI-SMM ассистент.</b>\n\n"
        "Я помогаю автоматизировать рутину в Telegram: переведу ваши "
        "видео в готовые тексты, подготовлю контент-план и адаптирую "
        "подачу под стиль вашего канала.\n\n"
        "Давайте начнем. Выберите нужное действие в меню ниже:"
    )

    if edit:
        await message.edit_text(text=text, reply_markup=main_menu(), parse_mode="HTML")
        return None

    await message.answer(text=text, reply_markup=main_menu(), parse_mode="HTML")
    await get_or_create_session(user_id=message.from_user.id)


@navigation_router.message(Command("start"))
async def start_by_command(message: Message, state: FSMContext, bot: Bot) -> None:
    await cleanup_media_messages(bot=bot, chat_id=message.chat.id, state=state)
    await state.clear()
    await cmd_start(message)



@navigation_router.callback_query(F.data.in_([CallbacksNavigation.MAIN_MENU, CallbacksStyle.CAT_BACK]))
async def start_by_button(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    await cleanup_media_messages(bot=bot, chat_id=callback.message.chat.id, state=state)
    await state.clear()
    await cmd_start(callback.message, edit=True)