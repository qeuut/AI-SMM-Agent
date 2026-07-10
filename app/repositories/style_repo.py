import json
import logging
from AI_SMM_AGENT.app.repositories.database import get_db


logger = logging.getLogger(__name__)


async def load_brand_style(user_id: int) -> dict[str, str] | None:
    db = await get_db()
    cursor = await db.execute("SELECT style_data FROM brand_settings WHERE user_id = ?", (user_id,))
    row = await cursor.fetchone()

    if row:
        return json.loads(row["style_data"]) # "style_data" вместо 0 потому что aiosqlite.Row - а значит теперь row = await cursor.fetchone() всегда возвращает dict вместо tuple()

    else:
        return None


async def save_brand_style(user_id: int, style_data: dict[str, str]) -> None:
    db = await get_db()
    style_json = json.dumps(style_data, ensure_ascii=False)
    logger.info(f"Сохранение в БД: user_id={user_id}, data={style_json}")
    await db.execute("INSERT OR REPLACE INTO brand_settings (user_id, style_data) VALUES (?, ?)",
                     (user_id, style_json))
    await db.commit()
    logger.info("Сохранено успешно")