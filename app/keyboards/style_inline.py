# сторонние библиотеки
import logging
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

# библиотеки с проекта
from AI_SMM_AGENT.app.models.callbacks import CallbacksStyle


# функция для группы кнопок cat__
from AI_SMM_AGENT.app.keyboards.general_inline import style_menu


logger = logging.getLogger(__name__)


STYLE_TRANSLATIONS = {
    "tone": {
        "friendly": "Дружелюбный",
        "expert": "Экспертный",
        "neutral": "Нейтральный",
        "custom": "Свой",
    },
    "emoji": {
        "lots": "Много",
        "mid": "Умеренно",
        "none": "Без эмодзи",
        "custom": "Свой",
    },
    "length": {
        "long": "Развернутые",
        "mid": "Средние",
        "short": "Короткие",
        "custom": "Свой",
    },
    "hashtags": {
        "auto": "Автоматически",
        "none": "Без хештегов",
        "custom": "Свой",
    },
    "cta": {
        "always": "Всегда",
        "sometimes": "Иногда",
        "never": "Никогда",
        "custom": "Свой",
    },
    "formality": {
        "formal": "Официальный",
        "neutral": "Нейтральный",
        "casual": "Разговорный",
        "custom": "Свой",
    },
    "addressing": {
        "you": "На ты",
        "vy": "На вы",
        "neutral": "Нейтрально",
        "custom": "Свой"
    }
}


CATEGORY_LABELS = {
    "tone": "📝 Тональность",
    "emoji": "😊 Эмодзи",
    "length": "📏 Длина постов",
    "hashtags": "#️⃣ Хештеги",
    "cta": "📢 Призыв (CTA)",
    "formality": "👔 Формальность",
    "brand_character": "🎭 Характер бренда",
    "banned": "🚫 Запрещённые темы",
    "addressing": "💬 Тип обращения"
}


style_buttons = {
    # Категории
    CallbacksStyle.CAT__TONE: "🎭 Тональность",
    CallbacksStyle.CAT__EMOJI: "✨ Эмодзи",
    CallbacksStyle.CAT__LENGTH: "📏 Длина постов",
    CallbacksStyle.CAT__HASHTAGS: "#️⃣ Хештеги",
    CallbacksStyle.CAT__CTA: "🎯 Призыв к действию (CTA)",
    CallbacksStyle.CAT__FORMALITY: "👔 Формальность",
    CallbacksStyle.CAT__BRAND_CHARACTER: "🧬 Характер бренда",
    CallbacksStyle.CAT__BANNED: "🚫 Запрещённые темы",
    CallbacksStyle.CAT__ADDRESSING: "💬 Обращение",
    CallbacksStyle.CAT__CUSTOM: "✏️ Написать свой общий стиль",
    CallbacksStyle.CAT_BACK: "⬅️ Вернуться в главное меню",

    # Тональность
    CallbacksStyle.TONE_FRIENDLY: "🤝 Дружелюбный",
    CallbacksStyle.TONE_EXPERT: "💡 Экспертный",
    CallbacksStyle.TONE_NEUTRAL: "⚖️ Нейтральный",
    CallbacksStyle.TONE_CUSTOM: "⚙️ Написать свой тип",
    CallbacksStyle.TONE_BACK: "⬅️ Вернуться в меню настроек стиля",

    # Эмодзи
    CallbacksStyle.EMOJI_LOTS: "💥 Много",
    CallbacksStyle.EMOJI_MID: "✨ Умеренно",
    CallbacksStyle.EMOJI_NONE: "❌ Без эмодзи",
    CallbacksStyle.EMOJI_CUSTOM: "🔢 Указать конкретное количество",
    CallbacksStyle.EMOJI_BACK: "⬅️ Вернуться в меню настроек стиля",

    # Длина
    CallbacksStyle.LENGTH_LONG: "📝 Развернутые",
    CallbacksStyle.LENGTH_MID: "📐 Средние",
    CallbacksStyle.LENGTH_SHORT: "⏱ Короткие",
    CallbacksStyle.LENGTH_CUSTOM: "⚙️ Указать свой размер",
    CallbacksStyle.LENGTH_BACK: "⬅️ Вернуться в меню настроек стиля",

    # Хэштеги
    CallbacksStyle.HASHTAGS_AUTO: "🤖 Автоматически",
    CallbacksStyle.HASHTAGS_NONE: "❌ Без хештегов",
    CallbacksStyle.HASHTAGS_CUSTOM: "⚙️ Свой вариант",
    CallbacksStyle.HASHTAGS_BACK: "⬅️ Вернуться в меню настроек стиля",

    # CTA
    CallbacksStyle.CTA_ALWAYS: "📢 Всегда",
    CallbacksStyle.CTA_SOMETIMES: "🔄 Иногда",
    CallbacksStyle.CTA_NEVER: "❌ Никогда",
    CallbacksStyle.CTA_CUSTOM: "⚙️ Свой вариант",
    CallbacksStyle.CTA_BACK: "⬅️ Вернуться в меню настроек стиля",

    # Формальность
    CallbacksStyle.FORMALITY_FORMAL: "👔 Официальный",
    CallbacksStyle.FORMALITY_NEUTRAL: "⚖️ Нейтральный",
    CallbacksStyle.FORMALITY_CASUAL: "👕 Разговорный",
    CallbacksStyle.FORMALITY_CUSTOM: "⚙️ Свой вариант",
    CallbacksStyle.FORMALITY_BACK: "⬅️ Вернуться в меню настроек стиля",

    # Характер бренда
    CallbacksStyle.BRAND_CHARACTER_BACK: "⬅️ Вернуться в меню настроек стиля",

    # Запрещённые темы
    CallbacksStyle.BANNED_BACK: "⬅️ Вернуться в меню настроек стиля",

    # Обращение
    CallbacksStyle.ADDRESSING_YOU: "👤 На ты",
    CallbacksStyle.ADDRESSING_VY: "👥 На вы",
    CallbacksStyle.ADDRESSING_NEUTRAL: "🌐 Нейтрально (без местоимений)",
    CallbacksStyle.ADDRESSING_CUSTOM: "✏️ Написать свой вариант",
    CallbacksStyle.ADDRESSING_BACK: "⬅️ Вернуться в меню настроек стиля",
}



def creating_style_buttons(
        group_buttons: str,
        current_value: str | None = None
) -> InlineKeyboardMarkup:

    if group_buttons.startswith("cat"):
        logger.debug("group_buttons startswith cat")
        return style_menu()

    kb = InlineKeyboardBuilder()

    buttons = [
        (callback, text)
        for callback, text in style_buttons.items()
        if callback.startswith(f"{group_buttons}_")
    ]

    if not buttons:
        logger.error(
            "Button error in group '%s' :: creating_style_buttons",
            group_buttons
        )

        kb.button(
            text="Ошибка генерации кнопки, вернуться назад ⬅️",
            callback_data="MainMenu"
        )

        kb.adjust(1)
        return kb.as_markup()

    for callback, text in buttons:

        is_selected = (
            current_value is not None
            and current_value != "-"
            and callback.endswith(current_value)
        )

        kb.button(
            text=f"{text} ✅" if is_selected else text,
            callback_data=callback
        )

    kb.adjust(1)

    return kb.as_markup()