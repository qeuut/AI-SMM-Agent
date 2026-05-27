# Стандартные библиотеки
import logging

# Сторонние библиотеки
from aiogram import Router, F
from aiogram.types import CallbackQuery

# Клавиатуры
from AI_SMM_AGENT.app.keyboards import back_to
from AI_SMM_AGENT.app.keyboards.settings_inline import(
    settings_main_btn, settings_select_publication_mode,
    settings_select_channel, settings_back_to,
)

# модели
from AI_SMM_AGENT.app.models.callbacks import CallbacksSettings

settings_router = Router()


logger = logging.getLogger(__name__)


@settings_router.callback_query(F.data == CallbacksSettings.SETTINGS)
async def settings_cmd(callback: CallbackQuery) -> None:
    text = (
        "<b>⚙️ Параметры и настройки</b>\n\n"
        "В этом разделе вы можете управлять конфигурацией вашего профиля: "
        "привязать целевой Telegram-канал, выбрать формат автоматического "
        "постинга или ознакомиться с инструкцией.\n\n"
        "Выберите нужный раздел:"
    )

    await callback.message.edit_text(text=text,
                                     reply_markup=settings_main_btn(),
                                     parse_mode="HTML")


@settings_router.callback_query(F.data == CallbacksSettings.PUBLICATION_MODE_SETTINGS)
async def cmd_publication_mode_settings(callback: CallbackQuery) -> None:
    await callback.message.edit_text(text="DEBUG: <b>🤖 Режим публикации</b>",
                                     reply_markup=settings_select_publication_mode(),
                                     parse_mode="HTML")


@settings_router.callback_query(F.data == CallbacksSettings.SELECT_CHANNEL_SETTINGS)
async def cmd_select_channel_settings(callback: CallbackQuery) -> None:
    await callback.message.edit_text(text="DEBUG: <b>📢 Выбор канала</b>",
                                     reply_markup=settings_select_channel(),
                                     parse_mode="HTML")


@settings_router.callback_query(F.data == CallbacksSettings.HELP_SETTINGS)
async def cmd_help_settings(callback: CallbackQuery) -> None:
    await callback.message.edit_text(text="<b>ℹ️ О боте / Помощь</b>",
                                     reply_markup=settings_back_to(text="⬅️ Вернуться в настройки", callback="settings"),
                                     parse_mode="HTML")
