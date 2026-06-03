import logging
from aiogram.types import InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder


logger = logging.getLogger(__name__)

# часто используемые функции
def back_to(text: str ="⬅️ Вернуться в главное меню", callback_data: str ="MainMenu") -> InlineKeyboardMarkup:
    return create_buttons(texts=[text], callbacks=[callback_data])


def create_buttons(
    texts: list[str],
    callbacks: list[str],
    adjust: int = 1,
    net: list[int] | None = None
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()

    try:
        if not texts or not callbacks or len(texts) != len(callbacks):
            raise ValueError(
                f"Payload mismatch: texts={len(texts) if texts else 0}, callbacks={len(callbacks) if callbacks else 0}"
            )

        if net is not None:
            if sum(net) != len(texts):
                raise ValueError( # anti patern - fix this
                    f"Net mismatch: sum(net)={sum(net)}, buttons={len(texts)}"
                )

        for text, cb in zip(texts, callbacks):
            safe_text = str(text)
            safe_cb = str(cb)

            if len(safe_cb.encode("utf-8")) > 64:
                logger.warning(f"Callback data too long: {safe_cb}")
                safe_cb = "error_too_long"

            builder.button(text=safe_text, callback_data=safe_cb)

        if net is not None:
            builder.adjust(*net)
        else:
            builder.adjust(adjust if adjust > 0 else 1)

    except Exception as e: # anti patern - fix this
        logger.error(f"Keyboard Generation Error: {e}")
        builder = InlineKeyboardBuilder()
        builder.button(text="⬅️ В главное меню", callback_data="MainMenu")

    return builder.as_markup()