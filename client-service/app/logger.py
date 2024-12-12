import logging
from logging.handlers import RotatingFileHandler


# Настраиваем логгер
logger = logging.getLogger("app_logger")
logger.setLevel(logging.DEBUG)

# Формат логов
formatter = logging.Formatter(
    "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Консольный обработчик
console_handler = logging.StreamHandler()
console_handler.setFormatter(formatter)


# Файловый обработчик (с ротацией файлов)
file_handler = RotatingFileHandler(
    "app.log", maxBytes=5 * 1024 * 1024, backupCount=2
)
file_handler.setFormatter(formatter)

# Добавляем обработчики в логгер
logger.addHandler(console_handler)
logger.addHandler(file_handler)
