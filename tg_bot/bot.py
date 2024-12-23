from abc import ABC, abstractmethod
from datetime import datetime
from typing import Optional

from aiogram import Bot, types
from .constants import HELP_MESSAGE, START_MESSAGE, RESULT_NONE_MESSAGE
from .database import BotDatabase
from .structs import SearchEntity, Movie, Banner, StatsEntity
from .search import SearchEngine
from .helpers import merge_movies, movie_to_banner, first_non_none
from .scrapper import Scrapper


class BotApi(ABC):

    @abstractmethod
    async def handle_start(self, message: types.Message) -> None:
        pass

    @abstractmethod
    async def handle_help(self, message: types.Message) -> None:
        pass

    @abstractmethod
    async def handle_history(self, message: types.Message) -> None:
        pass

    @abstractmethod
    async def handle_stats(self, message: types.Message) -> None:
        pass

    @abstractmethod
    async def handle_search(self, message: types.Message) -> None:
        pass



class BotApiImpl(BotApi):
    site_to_watch_online: str = "rutube.ru"

    def __init__(self, bot: Bot, database: BotDatabase, engines: dict[str, SearchEngine], scrapper: Scrapper):
        self.bot = bot
        self.database = database
        self.engines = engines
        self.scrapper = scrapper

    async def handle_start(self, message: types.Message) -> None:
        await self.bot.send_message(message.chat.id, START_MESSAGE)

    async def handle_help(self, message: types.Message) -> None:
        await self.bot.send_message(message.chat.id, HELP_MESSAGE)

    async def handle_history(self, message: types.Message) -> None:
        history: list[SearchEntity] = await self.database.load_search_entities(message.chat.id)
        if history:
            result = '\n'.join(reversed([self._search_entity_to_str(item) for item in history]))
        else: 
            result = "\nИстория пуста." 
        await self.bot.send_message(message.chat.id, result)

    async def handle_stats(self, message: types.Message) -> None:
        stats: list[StatsEntity] = await self.database.load_stats_entities(message.chat.id)
        stats = sorted(stats, key=lambda item: -item.count)
        if stats:
            result = '\n'.join([self._stats_entity_to_str(item) for item in stats])
        else:
            result = "\nСтатистика пуста."
        await self.bot.send_message(message.chat.id, result)

    async def handle_search(self, message: types.Message) -> None:
        args = message.text
        if not args:
            await self.bot.send_message(message.chat.id, "Пожалуйста, укажите запрос для поиска.")
            return

        result: Optional[Movie] = None
        result_kp: Optional[Movie] = await self.engines['kinopoisk'].search_movie(args)

        if result_kp:
            result = merge_movies([result_kp])
        else:
            result = first_non_none([result_kp])

        if result is None:
            await self.bot.send_message(message.chat.id, RESULT_NONE_MESSAGE)
            return

        result.links_to_watch = [self.scrapper.get_top_link(str(result.title))]

        #await self.bot.send_message(message.chat.id, str(result.links_to_watch))

        banner: Banner = movie_to_banner(result)

        if banner.picture:
            await self.bot.send_photo(message.chat.id, banner.picture, caption=banner.text, parse_mode='Markdown')
        else:
            await self.bot.send_message(message.chat.id, banner.text, parse_mode='Markdown')

        search_entity = SearchEntity(
            message.chat.id,
            args,
            str(result.title),
            datetime.now(),
            result.id_kp
        )
        await self.database.save_search_entity(search_entity)


    @staticmethod
    def _search_entity_to_str(entity: SearchEntity) -> str:
        return f'{entity.datetime}: {entity.text} -> "{entity.title}"'

    @staticmethod
    def _stats_entity_to_str(entity: StatsEntity) -> str:
        return f'{entity.title}: {entity.count}'