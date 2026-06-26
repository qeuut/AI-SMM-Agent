import logging
import aiosqlite
from pathlib import Path


logger = logging.getLogger(__name__)


DB_PATH = Path(__file__).parent.parent.parent / "data" / "app.db"


_db: aiosqlite.Connection | None = None


async def get_db() -> aiosqlite.Connection:
    if _db is None:
        raise RuntimeError("DB not initialized. Call init_db() first.")
    return _db


async def connect_db() -> None:
    global _db
    _db = await aiosqlite.connect(DB_PATH)
    _db.row_factory = aiosqlite.Row  # строки как dict удобнее


async def disconnect_db() -> None:
    global _db
    if _db:
        await _db.close()
        _db = None


async def init_db() -> None: # открываем асинхронное соединение с БД на все время работы
    db = await get_db()
    await db.execute('''
                CREATE TABLE IF NOT EXISTS brand_settings (
                    user_id INTEGER PRIMARY KEY,
                    style_data TEXT NOT NULL DEFAULT '{}'
                )
            ''')
    await db.execute('''
                CREATE TABLE IF NOT EXISTS posts (
                    user_id INTEGER,
                    post_id INTEGER PRIMARY KEY AUTOINCREMENT,
                    draft_json TEXT, 
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    scheduled_at TIMESTAMP DEFAULT NULL,
                    published_at TIMESTAMP DEFAULT NULL,
                    status TEXT NOT NULL DEFAULT 'draft',
                    channel_message_ids TEXT DEFAULT NULL
                ) 
            ''') # statuses: 'draft', 'ready', 'published', 'scheduled'

    await db.execute('''
                    CREATE TABLE IF NOT EXISTS user_info (
                        user_id INTEGER PRIMARY KEY,
                        session_id INTEGER,
                        channel_id INTEGER
                    )
                ''')

    # await db.execute('''
    #                 CREATE TABLE IF NOT EXISTS user_draft (
    #                     user_id INTEGER PRIMARY KEY,
    #                     time_created,
    #                     draft)''')

    try:
        await db.execute('ALTER TABLE posts ADD COLUMN message_ids TEXT DEFAULT NULL')
        await db.commit()
    except Exception:
        pass  # - колонка существует

    await db.commit()
    await db.execute('CREATE INDEX IF NOT EXISTS idx_posts_user_status ON posts(user_id, status)')
    await db.commit()
