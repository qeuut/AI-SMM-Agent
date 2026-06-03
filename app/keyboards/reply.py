from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, KeyboardButtonRequestChat

def get_change_channel_reply_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            # Первая строчка: главная кнопка запроса канала
            [
                KeyboardButton(
                    text="📢 Выбрать / Сменить канал",
                    request_chat=KeyboardButtonRequestChat(
                        request_id=1,          # Любое число-идентификатор
                        chat_is_channel=True,   # Ищем именно КАНАЛЫ (не группы)
                        bot_is_member=False,    # Бот может пока не быть участником
                        user_privileges=None    # Любой канал, где юзер админ
                    )
                )
            ],
            # Вторая строчка: обычная текстовая кнопка отмены
            [
                KeyboardButton(text="❌ Отменить и вернуться в меню настроек")
            ]
        ],
        resize_keyboard=True,
        one_time_keyboard=True
    )


def get_main_menu_reply_keyboard():
    return ReplyKeyboardMarkup(
        keyboard=[
            [
                KeyboardButton(text="⬅️ Вернуться в главное меню")
            ]
        ],
        resize_keyboard=True
    )
