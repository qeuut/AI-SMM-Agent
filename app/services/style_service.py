from AI_SMM_AGENT.app.keyboards import back_to
from AI_SMM_AGENT.app.keyboards.style_inline import creating_style_buttons
from AI_SMM_AGENT.app.services.saved_style import set_style
from aiogram.types import InlineKeyboardMarkup
from AI_SMM_AGENT.app.services.saved_style import get_style
from AI_SMM_AGENT.app.keyboards.style_inline import CATEGORY_LABELS, STYLE_TRANSLATIONS
from AI_SMM_AGENT.app.UI.style import texts_for_messages
import logging


logger = logging.getLogger(__name__)




async def build_style_menu_text(user_id: int, changed_now: str = ""):
    """Возвращает текст для главного меню настроек с текущими параметрами из БД"""

    if not user_id:
        logger.error("Функция ---build_style_menu_text--- ошибка, аргумент user_id - пуст")
        return "Произошла непредвиденная ошибка, попробуйте снова..."

    style = await get_style(user_id)
    style_text = ""

    for key, value in CATEGORY_LABELS.items():
        if key in style:
            if key in STYLE_TRANSLATIONS:
                translated = STYLE_TRANSLATIONS[key].get(style[key], style[key])
            else:
                translated = style[key]  # для brand_character, banned — показываем как есть

            changed_now_suffix = "\n<b>└─ Обновлено только что</b>" if changed_now == key else ""
            logger.debug(f"{changed_now, key}")
            style_text += f"{value}: {translated + changed_now_suffix}\n" # добавить обработку: translated if translated < X symbols else translated[:60]
        else:
            style_text += f"{value}: <i>Не указано</i>\n"

    base_text = texts_for_messages["cat"]

    return (
        f"{base_text}\n\n"
        f"<b>Ваши текущие настройки:</b>\n"
        f"{style_text.strip()}"
    )