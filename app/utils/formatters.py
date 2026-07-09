from typing import Optional
from aiogram.types import Message


from AI_SMM_AGENT.app.models.stat_of_post import ReturnedPostStat



def format_statistics_text(post_statistics: ReturnedPostStat) -> str:
    fmt = "%d.%m.%Y %H:%M"
    last_date = (
        post_statistics.last_post_date.strftime(fmt) if post_statistics.last_post_date else "—"
    )
    scheduled_date = (
        post_statistics.last_scheduled_post_date.strftime(fmt)
        if post_statistics.last_scheduled_post_date
        else "Нет"
    )
    published_date = (
        post_statistics.last_published_post_date.strftime(fmt)
        if post_statistics.last_published_post_date
        else "Нет"
    )

    return (
        "<b>📊 Статистика канала</b>\n\n"
        "В этом разделе вы можете оценить эффективность вашего контента, "
        "посмотреть охваты и получить персональные советы от искусственного "
        "интеллекта по улучшению показателей.\n\n"
        "<b>📈 Общие показатели:</b>\n"
        f"- Всего постов сгенерировано: <code>{post_statistics.quantity_posts}</code>\n"
        f"- Сейчас запланировано: <code>{post_statistics.quantity_scheduled}</code>\n"
        f"- Уже опубликовано: <code>{post_statistics.quantity_published}</code>\n\n"
        "<b>📝 Последняя активность:</b>\n"
        f"- Текст: <i>«{post_statistics.last_post_about}»</i>\n"
        f"- Статус: <b>{post_statistics.last_post_status}</b>\n"
        f"- Дата изменения: <code>{last_date}</code>\n\n"
        "<b>📅 Даты последних выходов:</b>\n"
        f"- Крайний в очереди: <code>{scheduled_date}</code>\n"
        f"- Последний вышедший: <code>{published_date}</code>\n\n"
    )


def format_draft_added_text(album: Optional[list[Message]], quantity_photos: int, quantity_videos: int):
    if album:
            return (
                f"<b>✅ Альбом добавлен в черновик</b>\n\n"
                f"Успешно сохранено: фото — {quantity_photos}, видео — {quantity_videos}.\n\n"
                f"Вы можете отправить дополнительные материалы или нажать кнопку ниже для запуска генерации 👇"
            )
    else:
            return (
                "<b>✅ Материал добавлен в черновик</b>\n\n"
                "Ваше сообщение успешно сохранено. Вы можете отправить вдогонку дополнительные материалы "
                "(например, текст-пояснение или фотографии).\n\n"
                "Если все готово — нажмите кнопку ниже для запуска генерации 👇"
            )
















