# Стандартные библиотеки
import logging
from contextlib import suppress


# Сторонние библиотеки
from aiogram import Router, F, Bot
from aiogram.exceptions import TelegramAPIError
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message

# Клавиатуры
from AI_SMM_AGENT.app.keyboards import back_to
from AI_SMM_AGENT.app.keyboards.settings_inline import(
    settings_main_btn
)
from AI_SMM_AGENT.app.keyboards.reply import (
    get_change_channel_reply_keyboard, get_main_menu_reply_keyboard,

)

# модели
from AI_SMM_AGENT.app.models.callbacks import CallbacksSettings

# БД
from AI_SMM_AGENT.app.repositories.user_info_repo import save_channel_id

# utils
from AI_SMM_AGENT.app.utils.telegram_helpers import create_channel_changed_text

# texts
from AI_SMM_AGENT.texts.settings_texts import SETTINGS_ABOUT_BOT, SETTINGS_MENU


settings_router = Router()


logger = logging.getLogger(__name__)


async def settings_cmd(event: CallbackQuery | Message) -> None:
    if isinstance(event, CallbackQuery):
        await event.message.edit_text(text=SETTINGS_MENU,
                                      reply_markup=settings_main_btn(),
                                      parse_mode="HTML")

    elif isinstance(event, Message):
        try:
            await event.delete()
        except TelegramAPIError:
            logger.warning(f"Функция ---settings_cmd---, event = {event}, ошибка во время удаления сообщения...")

        await event.answer(text=SETTINGS_MENU,
                           reply_markup=settings_main_btn(),
                           parse_mode="HTML")


@settings_router.callback_query(F.data == CallbacksSettings.SETTINGS)
async def calling_setting_cmd_by_inline(callback: CallbackQuery):
    await settings_cmd(callback)


@settings_router.message(F.text == "❌ Отменить и вернуться в меню настроек")
async def calling_setting_cmd_by_reply(message: Message, state: FSMContext):
    data = await state.get_data()
    mssg_id = data.get("select_channel_mssg_id")

    if mssg_id:
        with suppress(TelegramAPIError):
            await message.bot.delete_message(message.chat.id, mssg_id)

    await settings_cmd(message)
    await state.update_data(reply_keyboard_status=False)


@settings_router.callback_query(F.data == CallbacksSettings.SELECT_CHANNEL_SETTINGS)
async def cmd_select_channel_settings(callback: CallbackQuery, state: FSMContext) -> None:
    try:
        await callback.message.delete() # Удаляем последнее и шлем новое т.к., reply кнопку нельзя делать вместе с edit_text
    except TelegramAPIError:
        logger.error(f"Функция ---cmd_select_channel_settings--- ошибка во время удаления сообщения с ID {callback.message.message_id}")

    sent = await callback.message.answer(text="<b>📢 Выбор канала</b>\n\n" # Шлем новое т.к., reply кнопку нельзя делать вместе с edit_text
                                              "В меню ниже: после нажатия на кнопку выберете нужный вам канал",
                                         reply_markup=get_change_channel_reply_keyboard(),
                                         parse_mode="HTML")

    await state.update_data(select_channel_mssg_id=sent.message_id)
    await state.update_data(reply_keyboard_status=True)


@settings_router.message(F.chat_shared)
async def handle_shared_chat(message: Message, state: FSMContext, bot: Bot):
    # Вытаскиваем ID и название канала, который выбрал пользователь
    new_channel_id = message.chat_shared.chat_id

    final_text = await create_channel_changed_text(bot=bot, new_channel_id=new_channel_id)
    await save_channel_id(user_id=message.from_user.id, channel_id=new_channel_id)

    # Возвращаем пользователя в меню статистики или главное меню
    data = await state.get_data()
    mssg_id = data.get("select_channel_mssg_id")

    try:
        await bot.delete_message(message.chat.id, mssg_id)
    except TelegramAPIError:
        logger.error(f"Ошибка во время удаления сообщения с ID: {mssg_id}")

    await message.answer(final_text, parse_mode="HTML", reply_markup=get_main_menu_reply_keyboard())
    await state.update_data(reply_keyboard_status=True)

@settings_router.callback_query(F.data == CallbacksSettings.HELP_SETTINGS)
async def cmd_help_settings(callback: CallbackQuery) -> None:
    await callback.message.edit_text(text=SETTINGS_ABOUT_BOT,
                                     reply_markup=back_to(text="⬅️ Вернуться в меню настроек", callback_data="settings"),
                                     parse_mode="HTML")


@settings_router.callback_query(F.data == CallbacksSettings.NOTIFICATIONS)
async def notifications(callback: CallbackQuery):
    await callback.message.edit_text("DEBUG: Функция в разработке", reply_markup=back_to(
                                                                                text="⬅️ Вернуться в меню настроек",
                                                                                callback_data="settings"))