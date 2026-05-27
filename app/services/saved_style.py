import logging
from AI_SMM_AGENT.app.repositories.style_repo import load_brand_style, save_brand_style


logger = logging.getLogger(__name__)


async def get_style(user_id: int) -> dict[str, str]:
    check_value = await load_brand_style(user_id=user_id)

    if check_value:
        return check_value
    else:
        return {}


async def set_style(user_id: int, key: str, value: str) -> None:
    styles_settings = await get_style(user_id)
    styles_settings[key] = value

    await save_brand_style(user_id, styles_settings)