import logging
import asyncio

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