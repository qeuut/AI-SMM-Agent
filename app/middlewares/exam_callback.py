from aiogram.filters import Filter
from aiogram.types import CallbackQuery


class ValidCallbackFilter(Filter):
    async def __call__(self, query: CallbackQuery) -> bool:
        if not query.message:

            return False

        if query.data is None:
            return False

        return True
