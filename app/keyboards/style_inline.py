# сторонние библиотеки
import logging
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

# библиотеки с проекта
from AI_SMM_AGENT.app.models.callbacks import CallbacksStyle


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
    "cta": "📢 Призыв к действию (CTA)",
    "formality": "👔 Формальность",
    "brand_character": "🎭 Характер бренда",
    "banned": "🚫 Запрещённые темы",
    "addressing": "💬 Обращение к аудитории"
}


style_buttons = {
    # Категории
    CallbacksStyle.CAT__TONE: "📝 Тональность",
    CallbacksStyle.CAT__EMOJI: "😊 Эмодзи",
    CallbacksStyle.CAT__LENGTH: "📏 Длина постов",
    CallbacksStyle.CAT__HASHTAGS: " #️⃣ Хэштеги",
    CallbacksStyle.CAT__CTA: " 📢 Призыв к действию (CTA)",
    CallbacksStyle.CAT__FORMALITY: "👔 Формальность",
    CallbacksStyle.CAT__BRAND_CHARACTER: "🎭 Характер бренда",
    CallbacksStyle.CAT__BANNED: "🚫 Запрещённые темы",
    CallbacksStyle.CAT__ADDRESSING: "💬 Обращение",
    CallbacksStyle.CAT__CUSTOM: "Написать свой общий стиль",
    CallbacksStyle.CAT_BACK: "⬅️ Вернуться в главное меню",

    # Тональность
    CallbacksStyle.TONE_FRIENDLY: "Дружелюбный",
    CallbacksStyle.TONE_EXPERT: "Экспертный",
    CallbacksStyle.TONE_NEUTRAL: "Нейтральный",
    CallbacksStyle.TONE_CUSTOM: "Написать свой тип",
    CallbacksStyle.TONE_BACK: "⬅️ Вернуться назад",

    # Эмодзи
    CallbacksStyle.EMOJI_LOTS: "Много",
    CallbacksStyle.EMOJI_MID: "Умеренно",
    CallbacksStyle.EMOJI_NONE: "Без эмодзи",
    CallbacksStyle.EMOJI_CUSTOM: "Указать конкретное количество",
    CallbacksStyle.EMOJI_BACK: "⬅️ Вернуться назад",

    # Длина
    CallbacksStyle.LENGTH_LONG: "Развернутые",
    CallbacksStyle.LENGTH_MID: "Средние",
    CallbacksStyle.LENGTH_SHORT: "Короткие",
    CallbacksStyle.LENGTH_CUSTOM: "Указать свой размер",
    CallbacksStyle.LENGTH_BACK: "⬅️ Вернуться назад",

    # Хэштеги
    CallbacksStyle.HASHTAGS_AUTO: "Автоматически",
    CallbacksStyle.HASHTAGS_NONE: "Без хештегов",
    CallbacksStyle.HASHTAGS_CUSTOM: "Указать свои хэштеги",
    CallbacksStyle.HASHTAGS_BACK: "⬅️ Вернуться назад",

    # CTA
    CallbacksStyle.CTA_ALWAYS: "Всегда",
    CallbacksStyle.CTA_SOMETIMES: "Иногда",
    CallbacksStyle.CTA_NEVER: "Никогда",
    CallbacksStyle.CTA_CUSTOM: "Указать самостоятельно",
    CallbacksStyle.CTA_BACK: "⬅️ Вернуться назад",

    # Формальность
    CallbacksStyle.FORMALITY_FORMAL: "Официальный",
    CallbacksStyle.FORMALITY_NEUTRAL: "Нейтральный",
    CallbacksStyle.FORMALITY_CASUAL: "Разговорный",
    CallbacksStyle.FORMALITY_CUSTOM: "Написать свой вариант",
    CallbacksStyle.FORMALITY_BACK: "⬅️ Вернуться назад",

    # Характер бренда
    CallbacksStyle.BRAND_CHARACTER_CUSTOM: "Написать свой вариант", # исправить - ввод должен быть уже на этом этапе без доп. кнопок
    CallbacksStyle.BRAND_CHARACTER_BACK: "⬅️ Вернуться назад", # исправить - ввод должен быть уже на этом этапе без доп. кнопок

    # Запрещённые темы
    CallbacksStyle.BANNED_CUSTOM: "Написать свой список", # исправить - ввод должен быть уже на этом этапе без доп. кнопок
    CallbacksStyle.BANNED_BACK: "⬅️ Вернуться назад", # исправить - ввод должен быть уже на этом этапе без доп. кнопок

    # Обращение
    CallbacksStyle.ADDRESSING_YOU: "На ты",
    CallbacksStyle.ADDRESSING_VY: "На вы",
    CallbacksStyle.ADDRESSING_NEUTRAL: "Нейтрально (без местоимений)",
    CallbacksStyle.ADDRESSING_CUSTOM: "Написать свой вариант",
    CallbacksStyle.ADDRESSING_BACK: "⬅️ Вернуться назад",
}


def creating_style_buttons(
        group_buttons: str,
        current_value: str = "-"
)       -> InlineKeyboardMarkup:

    kb = InlineKeyboardBuilder()
    count_buttons = 0

    for key, value in style_buttons.items():
        if key.startswith(f"{group_buttons}_"): # _ - для обработки пустого аргумента

            label = (f"{value} ✅"
                     if key.endswith(current_value)
                     else value
            )

            kb.button(text=label,
                      callback_data=key
            )

            count_buttons += 1

    if count_buttons < 2: # 2 - так как это самое маленькое количество возможных кнопок
        logger.error(f"Button error in group {group_buttons} :: while creating button function --- creating_style_buttons ---"
        )

        kb = InlineKeyboardBuilder()

        kb.button(text="Ошибка генерации кнопки, вернуться назад ⬅️",
                  callback_data = "MainMenu"
        )

    kb.adjust(1)
    return kb.as_markup()