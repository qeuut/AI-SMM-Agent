from AI_SMM_AGENT.app.keyboards import back_to
from AI_SMM_AGENT.app.keyboards.style_inline import creating_style_buttons
from aiogram.types import InlineKeyboardMarkup
import logging


logger = logging.getLogger(__name__)


texts_for_messages = {
    "cat": "<b>🎨 Настройка стиля и тональности</b>\n\n"
    "Выберите параметр ниже, чтобы изменить его, или отправьте свой "
    "текстовый промт - ИИ будет использовать эти настройки при генерации "
    "каждого поста.",


    "tone": "Какая тональность постов вас устраивает?",
    "emoji": "Какая частота применения эмодзи вас устраивает?",
    "length": "Какая длина постов вас устраивает?",
    "hashtags": "Как много хештегов в постах должно быть?",
    "cta": "Как часто ИИ агент должен призывать к действию в своих постах?",
    "general": "Опишите общий стиль для постов в канале.",
    "formality": "Насколько формальным должен быть язык?",
    "brand_character": "Опиши характер бренда (например: серьёзный, дерзкий, заботливый).",
    "banned": "Какие темы или слова запрещены? (через запятую)",
    "addressing": "Как обращаться к аудитории?"
}


def get_buttons_and_text(group_buttons: str, value: str = "-") -> tuple[InlineKeyboardMarkup, str]:
    emergency_button = back_to()
    if not group_buttons:
        logger.error(f"Функция get_buttons_text, category = None")
        return emergency_button, "Произошла ошибка, попробуйте снова"

    buttons = creating_style_buttons(group_buttons=group_buttons, current_value=value)
    text = texts_for_messages.get(group_buttons, "Ошибка...")

    logger.debug(f"Функция ---get_buttons_and_text--- group_buttons = {group_buttons} | value = {value}")
    logger.debug(f"Функция ---get_buttons_and_text--- text = {text}")

    return buttons, text