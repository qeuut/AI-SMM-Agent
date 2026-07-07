import logging
import asyncio

from aiogram import Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardRemove, Message
from aiogram.exceptions import TelegramAPIError


logger = logging.getLogger(__name__)


async def clean_reply_keyboard_if_present(data: dict,message: Message) -> None:
    reply_keyboard_status = data.get("reply_keyboard_status")
    logger.debug(f"reply_keyboard_status = {reply_keyboard_status}")

    if not reply_keyboard_status:
        return # если reply клавиатуры нет просто выход

    text = "⌛"
    try:
        mssg = await message.answer(text=text, reply_markup=ReplyKeyboardRemove())
        await mssg.delete()
        logger.info(f"---clean_reply_keyboard--- Сообщение '{text}' (message_id: {mssg.message_id} было успешно удалено")
    except TelegramAPIError as e:
        logger.error(f"---clean_reply_keyboard--- Ошибка удаления сообщения {text} на стороне телеграм: {e}")


async def build_channel_changed_text(bot: Bot, new_channel_id) -> str:
    try:
        chat_info = await bot.get_chat(new_channel_id)
        channel_title = chat_info.title
        channel_username = f"@{chat_info.username}" if chat_info.username else "Приватный"
        channel_username_status = bool(chat_info.username)

        link = (f'> Ссылка: <b>{channel_username}</b>'
                if channel_username_status
                else '> Ссылка: <code>канал приватный</code>')

    except TelegramAPIError:
        link = "> Ссылка: <code>канал приватный</code>"
        channel_title = "Выбранный канал"

    text = (
        "<b>✅ Канал успешно изменен!</b>\n\n"
        f"> Название: <code>{channel_title}</code>\n"
        f"{link}\n"
        f"> ID: <code>{new_channel_id}</code>\n\n"
        "<i>⚠️ Не забудьте добавить бота в этот канал администратором, чтобы он мог публиковать посты.</i>"
    )

    return text