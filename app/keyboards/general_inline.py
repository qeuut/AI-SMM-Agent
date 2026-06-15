# сторонние библиотеки
import logging
from aiogram.types import InlineKeyboardMarkup

# функция для кнопок
from AI_SMM_AGENT.app.keyboards import create_buttons

# models - CallbackStyle
from AI_SMM_AGENT.app.models.callbacks import CallbacksStyle


logger = logging.getLogger(__name__)


def main_menu():
    return create_buttons(texts=["✍️ Создать пост",
                          "🗂️ Публикации",
                          "📊 Статистика",
                          "🎨 Стиль бренда",
                          "💡 Контент‑план",
                          "⚙️ Настройки"],
                          callbacks=["create_post",
                                     "publication",
                                     "statistics",
                                     "style_brand",
                                     "content_plan",
                                     "settings"],
                          net=[1,2,2,1]
                          )


def draft_post():
    return create_buttons(texts=["✨ Сгенерировать", "⬅️ Отменить и вернуться назад"],
                          callbacks=["generate_post", "create_post"]
                          )


def question_for_publication():
    return create_buttons(texts=["✅ Опубликовать", " ❌ Нет, вернутся назад", "⬅️ Нет, выйти в главное меню"],
                          callbacks=["publishing_post", "show_post", "MainMenu"]
                          )


def pre_procedural_actions():
    return create_buttons(texts=["🚀 Опубликовать сейчас", "✏️ Редактировать", "📅 Запланировать", "🔄 Сгенерировать заново", "⬅️ Отменить и вернуться назад"],
                          callbacks=["question_for_post", "edit_current_post", "schedule_post", "post_generate_again", "create_post"]
                          )

def publication_main():
    return create_buttons(texts=["📤 Очередь на публикацию", "📅 Запланировать новый", "✅ Опубликованные", "⬅️ Вернутся в главное меню"],
                          callbacks=["queue_publication", "schedule_post", "published_posts", "MainMenu"]
                          )


def publishing_post():
    return create_buttons(texts=["DEBUG: попробовать еще раз", "⬅️ Вернуться в начало публикации"],
                          callbacks=["publishing_post", "MainMenu"]
                          )

def edit_post_back_or_generate():
    return create_buttons(texts=["✨ Сгенерировать с правками","⬅️ Вернуться назад"], # ДОБАВИТЬ ПОДРОБНЫЕ НАСТРОЙКИ: ЗАПЛАНИРОВАТЬ И ДР
                          callbacks=["apply_edit","show_post"]
                          )
def edit_post_back():
    return create_buttons(texts=["⬅️ Вернуться назад"], # ДОБАВИТЬ ПОДРОБНЫЕ НАСТРОЙКИ: ЗАПЛАНИРОВАТЬ И ДР
                          callbacks=["show_post"]
                          )

def statistics_info_btn():
    return create_buttons(texts=["📈 Общая сводка за 30 дней", "🔍 По конкретному посту", "💡 Рекомендации ИИ", "⬅️ Вернутся в главное меню"],
                         callbacks=["statistic_of_thirty_days",
                                "statistics_of_specific_post",
                                "statistics_AI_recommendation",
                                "MainMenu"]
                         )


def clarifying_question():
    return create_buttons(texts=["↩️ Пропустить и сгенерировать как есть", "⬅️ Отменить и вернуться назад"],
                         callbacks=["generation_in_eny_case", "create_post"]
                         )

def skip_question_or_back():
    return create_buttons(texts=["DEBUG: ⏭️ Можно будет пропустить вопрос", "⬅️ Вернутся к началу публикации"],
                          callbacks=["skip_question_post", "publication"]
                          )


def retrying_request_and_back():
    return create_buttons(texts=["🔄 Попробовать снова", "⬅️ Вернуться в главное меню"],
                          callbacks=["retry_request_to_n8n", "MainMenu"]) # ============================================================================================================= ТУТ ЗАГЛУШКА


def manage_current_post():
    return create_buttons(texts=["❌ Удалить пост с канала", "⬅️ Вернуться в главное меню"], #
                          callbacks=["-", "MainMenu"])


def y_or_n(callbacks: list[str]):
    if len(callbacks) == 2:
        return create_buttons(texts=["✅ Да", "❌ Нет"], callbacks=[callbacks[0], callbacks[1]])

    else:
        logger.error("Функция ---y_or_n--- файл ---general_inline--- список -callbacks- не равен 2 элементам")


def cancel_or_back():
    return create_buttons(texts=["❌ Отменить публикацию", "⬅️ Вернуться в главное меню"],
                          callbacks=["-", "MainMenu"]) # доделать отмену публикации (с предварительным вопросом перед отменой)

def create_post_or_back():
    return create_buttons(texts=["✨ Создать пост", "⬅️ Вернуться в меню публикаций"],
                          callbacks=["create_post", "publication"])


def style_menu():
    logger.debug(f"func ---style_menu--- values: CallbacksStyle.CAT__TONE{CallbacksStyle.CAT__TONE.value} CallbacksStyle.CAT__EMOJI{CallbacksStyle.CAT__EMOJI.value} CallbacksStyle.CAT_BACK{CallbacksStyle.CAT_BACK}")
    return create_buttons(
        texts=[
            "🎭 Тональность",      # 2 кнопки в ряд
            "✨ Эмодзи",
            "📏 Размер поста",      # 2 кнопки в ряд
            "#️⃣ Хештеги",
            "🎯 Призыв (CTA)", # 2 кнопки в ряд
            "👔 Формальность",
            "🧬 Лицо бренда",       # 2 кнопки в ряд
            "🗣 Обращения",
            "🚫 Стоп-слова", # 1 кнопка на всю ширину
            "✏️ Свой промт",   # 1 кнопка на всю ширину
            "⬅️ Вернуться в главное меню" # 1 кнопка на всю ширину
        ],
        callbacks=[
            CallbacksStyle.CAT__TONE.value,
            CallbacksStyle.CAT__EMOJI.value,
            CallbacksStyle.CAT__LENGTH.value,
            CallbacksStyle.CAT__HASHTAGS.value,
            CallbacksStyle.CAT__CTA.value,
            CallbacksStyle.CAT__FORMALITY.value,
            CallbacksStyle.CAT__BRAND_CHARACTER.value,
            CallbacksStyle.CAT__ADDRESSING.value,
            CallbacksStyle.CAT__BANNED.value,
            CallbacksStyle.CAT__CUSTOM.value,
            CallbacksStyle.CAT_BACK.value
        ],
        net=[2, 2, 2, 2, 2, 1]  # сетка
    )
