# Стандартные библиотеки
import logging
from contextlib import suppress

# Сторонние библиотеки
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.exceptions import TelegramBadRequest
from openai import base_url

# Клавиатуры
from AI_SMM_AGENT.app.keyboards.general_inline import (
    create_buttons, style_menu
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
from AI_SMM_AGENT.app.services.style_service import build_style_menu_text
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
    style, _ = callback.data.split("_")
    final_text = await build_style_menu_text(user_id=callback.from_user.id, changed_now=style)

    buttons, _ = get_buttons_and_text(group_buttons="cat")
    await callback.message.edit_text(text=final_text, reply_markup=buttons, parse_mode="HTML")


@style_router.callback_query(F.data.startswith(CallbacksStyle.CAT__SUFFIX))
async def select_style(callback: CallbackQuery, state: FSMContext) -> None:
    _, category  = callback.data.split("__")

    if category == CallbacksOther.CUSTOM: # выбрал написать промт
        await callback.message.edit_text("DEBUG: Напишите свой общий промт:",
                                         reply_markup=back_to(text="⬅️ Вернуться в меню настроек стиля",
                                                              callback_data="style_brand"))
        await state.set_state(SetStyleBrand.WritesCustomPrompt)
        return

    if category == CallbacksOther.BACK: # нажал кнопку назад
        await state.clear()
        return

    await state.update_data(which_style=category)

    buttons, text = get_buttons_and_text(group_buttons=category)

    await callback.message.edit_text(text=text, reply_markup=buttons)
    await state.set_state(SetStyleBrand.SelectCustomStyle)


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
    style, _ = callback.data.rsplit("_", 1) # 1 для обработки callback data по типу таких "brand_character_custom" с 2 "_" и больше
    logger.info(f"which_style = {style}")
    await state.update_data(which_style=style) # было - which_style=callback.data
    texts_directory = {
        "emoji": (
            "<b>✨ Настройка использования эмодзи</b>\n\n"
            "Введите желаемое количество или правила для смайликов. ИИ будет строго придерживаться этих рамок.\n"
            "<i>Пример:</i> <code>Максимум 3 штуки на пост, только в конце текста</code>"
        ),
        "tone": (
            "<b>🎭 Настройка стилистики и тональности</b>\n\n"
            "Опишите, в каком тоне бот должен общаться с аудиторией. Это определит атмосферу и выбор слов.\n"
            "<i>Пример:</i> <code>Экспертный, уверенный, без лишней воды и канцеляризмов</code>"
        ),
        "length": (
            "<b>📏 Настройка объема публикаций</b>\n\n"
            "Укажите желаемый размер постов. Вы можете задать его в символах, абзацах или в свободной форме.\n"
            "<i>Пример:</i> <code>Короткие заметки до 500 символов, емко и по делу</code>"
        ),
        "hashtags": (
            "<b>#️⃣ Настройка хештегов</b>\n\n"
            "Напишите правила генерации тегов. Укажите их количество, язык или перечислите обязательные теги.\n"
            "<i>Пример:</i> <code>3-5 релевантных тегов в самом конце публикации</code>"
        ),
        "cta": (
            "<b>🎯 Призывы к действию (CTA)</b>\n\n"
            "Укажите, к какому именно действию ИИ должен подталкивать читателя в самом конце публикации.\n"
            "<i>Пример:</i> <code>Вопрос для обсуждения в комментариях или ссылка на профиль</code>"
        ),
        "formality": (
            "<b>👔 Уровень формальности</b>\n\n"
            "Задайте рамки строгости текста. Это определит, насколько официальным будет язык генерации.\n"
            "<i>Пример:</i> <code>Полуформальный: уважительно, но простыми словами без сленга</code>"
        )
    }

    await callback.message.edit_text(text=texts_directory.get(style, "Напишите здесь свой параметр под этот стиль."),
                                  parse_mode="HTML",
                                  reply_markup=create_buttons(texts=["⬅️ Вернуться в меню настроек стиля"],
                                                              callbacks=[f"cat__{style}"]))
    await state.set_state(SetStyleBrand.SelectCustomStyle)


@style_router.message(SetStyleBrand.SelectCustomStyle)
async def save_custom_style(message: Message, state: FSMContext):
    data = await state.get_data()
    style_name = data.get("which_style")
    logger.info(f"saving style_name = {style_name}, value = {message.text}")
    await set_style(user_id=message.from_user.id, key=style_name, value=message.text)

    style_menu_text = await build_style_menu_text(user_id=message.from_user.id, changed_now=style_name)

    buttons, _ = get_buttons_and_text(group_buttons="cat")
    await message.answer(style_menu_text, parse_mode="HTML", reply_markup=buttons)

    await state.set_state(None)
    return

@style_router.message(SetStyleBrand.WritesCustomPrompt)
async def whites_custom_prompt(message: Message, state: FSMContext):
    await message.answer("Функция в разработке...", reply_markup=create_buttons(texts=["⬅️ Вернуться в меню настроек стиля"],
                                                                                    callbacks=["style_brand"]))

    # ОТПРАВКА ПРОМТА НА Н8Н НА ОЦЕНКУ
    ...
    ...
    ...


    # СОХРАНЕНИЕ ПРОМТА
    ...
    ...
    ...
