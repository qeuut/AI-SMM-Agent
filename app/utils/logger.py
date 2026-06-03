import logging
import sys
from pathlib import Path
import colorlog


LOG_DIR = Path("logs")
LOG_DIR.mkdir(exist_ok=True)

def setup_logger() -> logging.Logger:
    logger = logging.getLogger()
    logger.setLevel(logging.DEBUG) # минимально разрешенный уровень logger.debug для logs
    logging.getLogger("aiosqlite").setLevel(logging.INFO) # для библиотеки aiosqlite устанавливаем уровень не меньше чем INFO чтобы не засорять консоль

    formatter = colorlog.ColoredFormatter(
        "%(log_color)s%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        log_colors={
            'DEBUG': 'cyan',
            'INFO': 'green',
            'WARNING': 'yellow',
            'ERROR': 'red',
            'CRITICAL': 'red,bg_white',
        }
    )


    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    file_handler = logging.FileHandler(LOG_DIR / "bot.log", encoding="utf-8")
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    return logger

# Вызываем функцию настройки и получаем logger, который будем импортировать в других файлах
logger = setup_logger()