# Стандартные библиотеки
import logging
from contextlib import suppress

# Сторонние библиотеки
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest

# Клавиатуры
from AI_SMM_AGENT.app.keyboards.general_inline import (
    create_buttons
)
from AI_SMM_AGENT.app.keyboards import (
    back_to
)
from AI_SMM_AGENT.app.keyboards.style_inline import (
    STYLE_TRANSLATIONS, CATEGORY_LABELS
)

# Модели и Состояния
from AI_SMM_AGENT.app.utils.states import SetStyleBrand
from AI_SMM_AGENT.app.models.callbacks import CallbacksStyle, CallbacksOther

# Сервисы и Репозитории
from AI_SMM_AGENT.app.services.saved_style import set_style, get_style
# from AI_SMM_AGENT.app.services.style_service import

# middlewares, filters
from AI_SMM_AGENT.app.middlewares.callback_style_filter import CallbackFilters

# UI
from AI_SMM_AGENT.app.UI.style import get_buttons_and_text, texts_for_messages


style_router = Router()


logger = logging.getLogger(__name__)


@style_router.callback_query(F.data.in_(
                            [CallbacksStyle.STYLE_BRAND,
                             CallbacksStyle.TONE_BACK,
                             CallbacksStyle.EMOJI_BACK,
                             CallbacksStyle.LENGTH_BACK,
                             CallbacksStyle.HASHTAGS_BACK,
                             CallbacksStyle.CTA_BACK,
                             CallbacksStyle.FORMALITY_BACK,
                             CallbacksStyle.BRAND_CHARACTER_BACK,
                             CallbacksStyle.BANNED_BACK,
                             CallbacksStyle.ADDRESSING_BACK]))
async def style_brand(callback: CallbackQuery) -> None:
    style = await get_style(callback.from_user.id)
    style_text = ""

    for key, value in CATEGORY_LABELS.items():
        if key in style and key in STYLE_TRANSLATIONS:
            translated = STYLE_TRANSLATIONS[key].get(style[key], style[key])
            style_text += f"{value}: {translated}\n"
        else:
            # ИСПРАВЛЕНО: Добавлен тег курсива <i> для "Не указано"
            style_text += f"{value}: <i>Не указано</i>\n"

    base_text = texts_for_messages["cat"]

    # ИСПРАВЛЕНО: Упорядочены отступы \n для красивой иерархии в мессенджере
    final_text = (
        f"{base_text}\n\n"
        f"<b>Ваши текущие настройки:</b>\n"
        f"{style_text.strip()}"
    )

    buttons, _ = get_buttons_and_text(group_buttons="cat")
    await callback.message.edit_text(text=final_text, reply_markup=buttons, parse_mode="HTML")


@style_router.callback_query(F.data.startswith(CallbacksStyle.CAT__SUFFIX))
async def select_style(callback: CallbackQuery, state: FSMContext) -> None:
    _, category  = callback.data.split("__")

    if category == CallbacksOther.CUSTOM: # выбрал написать промт
        await callback.message.edit_text("DEBUG: Напишите свой общий промт:")
        await state.set_state(SetStyleBrand.WritesCustomPrompt)
        return

    if category == CallbacksOther.BACK: # нажал кнопку назад
        await state.clear()
        return

    buttons, text = get_buttons_and_text(group_buttons=category)
    await callback.message.edit_text(text=text, reply_markup=buttons)


@style_router.callback_query(lambda c: CallbackFilters.is_style(data=c.data))
async def processing_style(callback: CallbackQuery, state: FSMContext) -> None:
    logger.info(f"DEBUG: состояние: {state}")
    category, value = callback.data.split("_", 1)

    await set_style(callback.from_user.id, category, value)
    buttons, text = get_buttons_and_text(group_buttons=category, value=value)

    # на случай если пользователь нажал на ту кнопку где уже была галочка
    with suppress(TelegramBadRequest): # ------------------------------------------------------------ костыль, исправить
        await callback.message.edit_text(text=text, reply_markup=buttons) # ------------------------- костыль, исправить

    await callback.answer("Стиль сохранен...")


@style_router.callback_query(F.data.endswith(CallbacksStyle.CUSTOM_PREFIX))
async def processing_custom_styles(callback: CallbackQuery, state: FSMContext) -> None:
    style, _ = callback.data.split("_", 1) # 1 потому что нужно обрабатывать callback data по типу таких "brand_character_custom" [brand]= callback.data.split("_", 1)
    await state.update_data(which_style=style) # было - which_style=callback.data
    await callback.message.edit_text("Напишите здесь свой параметр под этот стиль.",
                                  reply_markup=create_buttons(texts=["⬅️ Вернуться назад"],
                                                              callbacks=[f"cat__{style}"]))
    await state.set_state(SetStyleBrand.SelectCustomStyle)


@style_router.message(SetStyleBrand.SelectCustomStyle)
async def save_custom_style(message: Message, state: FSMContext):
    data = await state.get_data()
    style_name = data.get("which_style")

    await set_style(user_id=message.from_user.id, key=style_name, value=message.text)
    await message.answer("Стиль успешно сохранен.", reply_markup=back_to())

    await state.set_state(None) # -------------------------------------------------------------------------------- КОСТЫЛЬ ИСПРАВИТЬ
    return

@style_router.message(SetStyleBrand.WritesCustomPrompt)
async def whites_custom_prompt(message: Message, state: FSMContext):
    await message.answer("Функция в разработке...", reply_markup=create_buttons(texts=["⬅️ Вернуться назад"],
                                                                                    callbacks=["style_brand"]))

    # ОТПРАВКА ПРОМТА НА Н8Н НА ОЦЕНКУ
    ...
    ...
    ...


    # СОХРАНЕНИЕ ПРОМТА
    ...
    ...
    ...
