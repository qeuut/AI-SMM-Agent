# Стандартные библиотеки
import logging
from contextlib import suppress


# Сторонние библиотеки
from aiogram import Router, F
from aiogram.exceptions import TelegramAPIError
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message, ReplyKeyboardRemove

# Клавиатуры
from AI_SMM_AGENT.app.keyboards import back_to
from AI_SMM_AGENT.app.keyboards.settings_inline import(
    settings_main_btn, settings_select_publication_mode
)
from AI_SMM_AGENT.app.keyboards.reply import (
    get_change_channel_reply_keyboard, get_main_menu_reply_keyboard,

)

# модели
from AI_SMM_AGENT.app.models.callbacks import CallbacksSettings


# состояния
from AI_SMM_AGENT.app.utils.states import SelectChannel

# БД
from AI_SMM_AGENT.app.repositories.user_info_repo import save_channel_id


settings_router = Router()


logger = logging.getLogger(__name__)


SETTINGS_ABOUT_BOT = (
    "<b>ℹ️ О боте</b>\n\n"

    "<b>Your AI SMM Agent</b> — AI-система для профессиональной работы с Telegram-контентом.\n\n"

    "Бот принимает ваши голосовые сообщения, наброски и медиафайлы, "
    "помогает находить идеи, создавать пошаговые <b>контент-планы</b> "
    "и писать готовые посты под <b>стиль вашего канала</b>.\n\n"

    "<blockquote>Система объединяет несколько AI-моделей в единую рабочую цепочку.</blockquote>\n\n"

    "Вместо базовых шаблонов здесь работает сеть <b>AI-агентов</b>: "
    "одни модули извлекают главные смыслы из ваших материалов, "
    "другие выстраивают четкую логику, а отдельные нейросети "
    "отвечают за качество текста и вовлечение аудитории.\n\n"

    "В результате вы получаете не просто автогенерацию, а глубоко проработанный SMM-контент.\n\n"

    "⚙️ <i>Проект находится в активной разработке.</i>\n"
    "Функции системы, сценарии работы и качество генерации "
    "постепенно улучшаются и расширяются."
)

SETTINGS_MENU = (
    "<b>⚙️ Параметры и настройки</b>\n\n"

    "Управление конфигурацией профиля и параметрами работы системы.\n\n"

    "В этом разделе можно:\n"
    "<b>></b> выбрать Telegram-канал для публикации\n"
    "<b>></b> ознакомиться с информацией о проекте\n\n"
)


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


# @settings_router.callback_query(F.data == CallbacksSettings.PUBLICATION_MODE_SETTINGS)
# async def cmd_publication_mode_settings(callback: CallbackQuery) -> None:
#     await callback.message.edit_text(text="<b>🤖 Режим публикации</b>",
#                                      reply_markup=settings_select_publication_mode(),
#                                      parse_mode="HTML")


@settings_router.callback_query(F.data == CallbacksSettings.SELECT_CHANNEL_SETTINGS)
async def cmd_select_channel_settings(callback: CallbackQuery, state: FSMContext) -> None:
    try:
        await callback.message.delete() # Удаляем последнее и шлем новое т.к., reply кнопку нельзя делать вместе с edit_text
    except TelegramAPIError:
        logger.error(f"Функция ---cmd_select_channel_settings--- ошибка во время удаления сообщения с ID {callback.message.message_id}")


    sent = await callback.message.answer(text="<b>📢 Выбор канала</b>\n\n"
                                              "В меню ниже: после нажатия на кнопку выберете нужный вам канал",
                                         reply_markup=get_change_channel_reply_keyboard(),
                                         parse_mode="HTML")

    await state.update_data(select_channel_mssg_id=sent.message_id)
    await state.update_data(reply_keyboard_status=True)


@settings_router.message(F.chat_shared)
async def handle_shared_chat(message: Message, state: FSMContext):
    # Вытаскиваем ID и название канала, который выбрал пользователь
    new_channel_id = message.chat_shared.chat_id

    try:
        chat_info = await message.bot.get_chat(new_channel_id)
        channel_title = chat_info.title
        channel_username = f"@{chat_info.username}" if chat_info.username else "Приватный"
        channel_username_status = bool(chat_info.username)

    except TelegramAPIError:
        channel_title = "Выбранный канал"
        channel_username = "Приватный"
        channel_username_status = False

    await save_channel_id(user_id=message.from_user.id, channel_id=new_channel_id)

    text = (
        "<b>✅ Канал успешно изменен!</b>\n\n"
        f"> Название: <code>{channel_title}</code>\n"
        f"{f'> Ссылка: <b>{channel_username}</b>' if channel_username_status else '> Ссылка: <code>канал приватный</code>'}\n"
        f"> ID: <code>{new_channel_id}</code>\n\n"
        "<i>⚠️ Не забудьте добавить бота в этот канал администратором, чтобы он мог публиковать посты.</i>"
    )

    # Возвращаем пользователя в меню статистики или главное меню
    data = await state.get_data()
    mssg_id = data.get("select_channel_mssg_id")

    try:
        await message.bot.delete_message(message.chat.id, mssg_id)
    except TelegramAPIError:
        logger.error(f"Функция ---handle_shared_chat--- ошибка во время удаления сообщения с ID: {mssg_id}")


    await message.answer(text, parse_mode="HTML", reply_markup=get_main_menu_reply_keyboard())
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