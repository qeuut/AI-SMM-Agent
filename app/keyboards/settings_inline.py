# сторонние библиотеки
import logging
from aiogram.types import InlineKeyboardMarkup

# импорты с проекта
from AI_SMM_AGENT.app.keyboards import create_buttons


logger = logging.getLogger(__name__)


def settings_main_btn():
    return create_buttons(
        texts=["🤖 Режим публикации", "📢 Выбор канала", "ℹ️ О боте / Помощь", "⬅️ Вернуться в настройки"],
        callbacks=["publication_mode_settings", "select_channel_settings", "help_settings", "MainMenu"]
    )


def settings_select_publication_mode():
    return create_buttons(
        texts=["DEBUG скоро тут появятся режимы", "DEBUG скоро тут появятся режимы", "⬅️ Вернуться в настройки"],
        callbacks=["None", "None", "settings"]
    )


def settings_select_channel():
    return create_buttons(
        texts=["DEBUG скоро тут появятся режимы", "DEBUG скоро тут появятся режимы", "⬅️ Вернуться в настройки"],
        callbacks=["None", "None", "settings"]
    )


def settings_back_to(text: str = "⬅️ Вернуться назад", callback: str | None = None):
    if not callback:
        callback = "settings"
        logger.error("Функция settings_back_to, не был передан аргумент callback, callback был взят как 'settings'")
        return

    return create_buttons(
        texts=[text],
        callbacks=[callback]
    )