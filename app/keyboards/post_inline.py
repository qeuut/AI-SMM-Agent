# сторонние библиотеки
import logging
from aiogram.types import InlineKeyboardMarkup

# функция для кнопок
from AI_SMM_AGENT.app.keyboards import create_buttons


logger = logging.getLogger(__name__)


# def back_or_retry():
#     return create_buttons(texts=["⬅️ Вернуться в главное меню", "🔄 Попробовать снова"],
#                           callbacks=["MainMenu", ""]
#                          )