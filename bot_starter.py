import asyncio
from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message
from tg_bot.bot import BotApi, BotApiImpl
from tg_bot.database import BotDatabase, BotDatabaseImpl
from tg_bot.search import SearchEngine, KpUnofficialSearchEngine
from tg_bot.scrapper import Scrapper, WebScrapper
from aiogram import Router


bot = Bot(token="7602699141:AAFdGcRRZN47yasYxxnE5WuVfumY91tVGTQ", proxy='http://proxy.server:8896')
router = Router()
dispatcher = Dispatcher()

database: BotDatabase = BotDatabaseImpl("C:\\Users\\gogid\\python\\cinemabot\\data\\database.db")

engines: dict[str, SearchEngine] = {
    'kinopoisk': KpUnofficialSearchEngine("83dc4665-f319-4840-8eb9-4728dd3a54fb")
}

scrapper: Scrapper = WebScrapper()

core: BotApi = BotApiImpl(bot, database, engines, scrapper)

known_commands: list[str] = ['start', 'help', 'stats', 'history']

@router.message(Command(commands=["start"]))
async def handle_start(message: Message):
    await core.handle_start(message)

@router.message(Command(commands=["help"]))
async def handle_help(message: Message):
    await core.handle_help(message)

@router.message(Command(commands=["stats"]))
async def handle_stats(message: Message):
    await core.handle_stats(message)

@router.message(Command(commands=["history"]))
async def handle_history(message: Message):
    await core.handle_history(message)

@router.message(F.text)
async def handle_search(message: Message):
    await core.handle_search(message)

async def main():
    dispatcher.include_router(router)
    print("Бот запущен. Ожидание сообщений...")
    await dispatcher.start_polling(bot)

if __name__ == '__main__':
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        print("Бот остановлен.")
