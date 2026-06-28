# сторонние библиотеки
import logging
from aiogram.types import InlineKeyboardMarkup

# импорты с проекта
from AI_SMM_AGENT.app.keyboards import create_buttons


logger = logging.getLogger(__name__)


def settings_main_btn():
    return create_buttons(
        texts=["📢 Telegram-канал", "🔔 Уведомления", "ℹ️ О боте / Помощь", "⬅️ Вернуться в главное меню"], # Уведомления: Включены
        callbacks=["select_channel_settings", "notifications", "help_settings", "MainMenu"],
        net=[2,1,1]
    )


def settings_select_publication_mode():
    return create_buttons(
        texts=["DEBUG скоро тут появятся режимы", "DEBUG скоро тут появятся режимы", "⬅️ Вернуться в настройки"],
        callbacks=["None", "None", "settings"]
    )