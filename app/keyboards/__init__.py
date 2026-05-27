import logging
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


logger = logging.getLogger(__name__)

# часто используемые функции
def back_to(text: str ="⬅️ Вернуться в главное меню", callback_data: str ="MainMenu") -> InlineKeyboardMarkup:
    return create_buttons(texts=[text], callbacks=[callback_data])


def create_buttons(texts: list[str], callbacks: list[str], adjust: int = 1) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    try:
        # Проверка на пустые данные или несоответствие длины
        if not texts or not callbacks or len(texts) != len(callbacks):
            raise ValueError(
                f"Payload mismatch: texts={len(texts) if texts else 0}, callbacks={len(callbacks) if callbacks else 0}")

        for text, cb in zip(texts, callbacks):
            # защита от чисел
            safe_text = str(text)
            safe_cb = str(cb)

            # ТГ -  callback_data не может быть > 64 байт
            if len(safe_cb.encode('utf-8')) > 64:
                logger.warning(f"Callback data too long: {safe_cb}")
                safe_cb = "error_too_long"

            builder.button(text=safe_text, callback_data=safe_cb)

        # 4. Валидация adjust
        builder.adjust(adjust if adjust > 0 else 1)

    except Exception as e:
        logger.error(f"Keyboard Generation Error: {e}")
        # Очищаем билдер и возвращаем безопасную кнопку
        builder = InlineKeyboardBuilder()
        builder.button(text="⬅️ В главное меню", callback_data="MainMenu")

    return builder.as_markup()