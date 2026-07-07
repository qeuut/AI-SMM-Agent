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
from AI_SMM_AGENT.app.repositories.sessionID_repo import get_or_create_session

# Текста
from AI_SMM_AGENT.texts.navigation_text import MAIN_MENU_TEXT

# Помощники
from AI_SMM_AGENT.app.utils.cleanup_media import cleanup_media_messages
from AI_SMM_AGENT.app.utils.telegram_helpers import clean_reply_keyboard_if_present

navigation_router = Router()


logger = logging.getLogger(__name__)


async def cmd_start(message: Message, state: FSMContext, user_id: int, edit: bool) -> None:
    data = await state.get_data()
    await state.clear()

    if edit:
        logger.info(f"Состояние для {user_id} было очищено")
        await message.edit_text(text=MAIN_MENU_TEXT,reply_markup=main_menu(),parse_mode="HTML")
        return None

    await clean_reply_keyboard_if_present(data=data, message=message)
    await get_or_create_session(user_id=user_id)
    await message.answer(text=MAIN_MENU_TEXT, reply_markup=main_menu(), parse_mode="HTML")


@navigation_router.message(Command("start"))
async def start_by_command(message: Message, state: FSMContext, bot: Bot) -> None:
    await cleanup_media_messages(bot=bot, chat_id=message.chat.id, state=state)
    await cmd_start(message, state=state, user_id=message.from_user.id, edit=False)


@navigation_router.callback_query(F.data.in_([CallbacksNavigation.MAIN_MENU, CallbacksStyle.CAT_BACK]))
async def start_by_inline_button(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    await cleanup_media_messages(bot=bot, chat_id=callback.message.chat.id, state=state)
    await cmd_start(message=callback.message, state=state, user_id=callback.from_user.id, edit=True)


@navigation_router.message(F.text == "⬅️ Вернуться в главное меню")
async def start_by_reply_button(message: Message, state: FSMContext) -> None:
    await cmd_start(message=message, state=state, user_id=message.from_user.id, edit=False)