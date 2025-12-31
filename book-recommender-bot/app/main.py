import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.client.default import DefaultBotProperties
from dotenv import load_dotenv
import os

from .bot_handlers import router
from .database import init_db

# Загрузка переменных окружения
load_dotenv()

# Настройка логирования
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/var/log/app/bot.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

async def main():
    """Основная функция запуска бота"""
    
    # Инициализация базы данных
    init_db()
    logger.info("Database initialized")
    
    # Инициализация бота
    bot_token = os.getenv('TELEGRAM_BOT_TOKEN')
    if not bot_token:
        logger.error("TELEGRAM_BOT_TOKEN not found in environment variables")
        return
    
    bot = Bot(
        token=bot_token,
        default=DefaultBotProperties(parse_mode='HTML')
    )
    
    # Инициализация хранилища (Redis)
    redis_url = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    storage = RedisStorage.from_url(redis_url)
    
    # Инициализация диспетчера
    dp = Dispatcher(storage=storage)
    dp.include_router(router)
    
    logger.info("Bot starting...")
    
    try:
        # Запуск бота
        await dp.start_polling(bot, allowed_updates=dp.resolve_used_update_types())
    except Exception as e:
        logger.error(f"Bot stopped with error: {e}")
    finally:
        await bot.session.close()
        logger.info("Bot stopped")

if __name__ == "__main__":
    asyncio.run(main())
