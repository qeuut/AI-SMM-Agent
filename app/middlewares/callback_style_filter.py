from AI_SMM_AGENT.app.models.callbacks import CallbacksStyle
import re


class CallbackFilters:
    @staticmethod
    def is_style(data: str) -> bool:
        # 1. Если строка пустая или в ней нет знака "_", сразу бракуем
        if not data or "_" not in data:
            return False

        # 2. Проверяем служебные исключения
        is_forbidden = data.startswith(("cat_", "cat__")) or data.endswith(("_custom", "_back"))

        # 3. Пропускаем только если это не запрещено
        return not is_forbidden


