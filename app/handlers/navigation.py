# Стандартные библиотеки
import logging

# Сторонние библиотеки
from aiogram import Router, F, Bot
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove

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

# модели
...

# Помощники
from AI_SMM_AGENT.app.utils.cleanup_media import cleanup_media_messages


navigation_router = Router()


logger = logging.getLogger(__name__)


async def cmd_start(message: Message, state: FSMContext, edit: bool = False) -> Message | None:
    if edit:
        await state.clear()
        logger.info(f"Состояние для {message.from_user.id} было очищено")
        await message.edit_text(text=MAIN_MENU_TEXT, reply_markup=main_menu(), parse_mode="HTML")
        return None

    data = await state.get_data()
    await state.clear() # дабы избежать 2-ых кликов по кнопке и 2-ых выполнений этой функции
    logger.debug(f"Состояние для {message.from_user.id} было очищено")

    reply_keyboard_status = data.get("reply_keyboard_status")

    if reply_keyboard_status:
        mssg = await message.answer(text="⌛", reply_markup=ReplyKeyboardRemove())
        await mssg.bot.delete_message(chat_id=message.chat.id, message_id=mssg.message_id)

    logger.debug(f"reply_keyboard_status = {reply_keyboard_status}")

    await message.answer(text=MAIN_MENU_TEXT, reply_markup=main_menu(), parse_mode="HTML")
    await get_or_create_session(user_id=message.from_user.id)


@navigation_router.message(Command("start"))
async def start_by_command(message: Message, state: FSMContext, bot: Bot) -> None:
    await cleanup_media_messages(bot=bot, chat_id=message.chat.id, state=state)
    await cmd_start(message, state=state)


@navigation_router.callback_query(F.data.in_([CallbacksNavigation.MAIN_MENU, CallbacksStyle.CAT_BACK]))
async def start_by_inline_button(callback: CallbackQuery, state: FSMContext, bot: Bot) -> None:
    await cleanup_media_messages(bot=bot, chat_id=callback.message.chat.id, state=state)
    await cmd_start(callback.message, state=state, edit=True)


@navigation_router.message(F.text == "⬅️ Вернуться в главное меню")
async def start_by_reply_button(message: Message, state: FSMContext, bot: Bot) -> None:
    await cmd_start(message=message, state=state)