from enum import Enum
from dataclasses import dataclass


class N8NStatus(Enum):
    CONNECTED = "connected"
    SUCCESS = "success"
    REJECTION = "rejection"
    QUESTION = "question"
    ERROR = "error"
    UNKNOWN = "unknown"

@dataclass
class N8NResult:
    status: N8NStatus # класс статусов
    post_text: str | None = None  # текст поста
    question_text: str | None = None # текст вопроса
    reason_reject_text: str | None = None # текст причины отказа
    style_warning: str | None = None # текст предупреждения о несоответствии стиля
    media_warning: str | None = None # текст предупреждения о несоответствии медиа
    final_text: str | None = None # финальный текст для отправки
    selected_file_ids: list[str] | None = None # выбранное медиа от юзера
    media_assessment: list[dict] | None = None # рекомендуемые медиа от ИИ

    # orig_post: dict | None = None # оригинальный пост если нужен