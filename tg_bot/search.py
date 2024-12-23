from abc import ABC, abstractmethod
from typing import Optional, Any

import aiohttp

from .structs import Movie
from .helpers import first_non_none


class SearchEngine(ABC):

    @abstractmethod
    async def search_movie(self, query: str) -> Optional[Movie]:
        pass


class KpUnofficialSearchEngine(SearchEngine):
    search_movie_endpoint: str = 'https://kinopoiskapiunofficial.tech/api/v2.1/films/search-by-keyword'
    get_movie_endpoint: str = 'https://kinopoiskapiunofficial.tech/api/v2.2/films'

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.headers = {
            'X-API-KEY': self.api_key,
            'Content-Type': 'application/json'
        }

    async def search_movie(self, query: str) -> Optional[Movie]:
        search_params = {
            'keyword': query,
            'page': 1
        }

        async with aiohttp.ClientSession(trust_env=True) as session:
            async with session.get(self.search_movie_endpoint, params=search_params, headers=self.headers) as response:
                if response.status != 200:
                    return None
                search_results = await response.json()

            movie_id = self._parse_top_movie_id(search_results)
            if not movie_id:
                return None

            async with session.get(f'{self.get_movie_endpoint}/{movie_id}', headers=self.headers) as response:
                if response.status != 200:
                    return None
                movie_details = await response.json()
                return self._parse_movie_json_obj(movie_details)

    @staticmethod
    def _parse_top_movie_id(json_response: dict[str, Any]) -> Optional[int]:
        films = json_response.get('films')
        if not films:
            return None
        top_film = films[0]
        return top_film.get('filmId')

    @staticmethod
    def _parse_movie_json_obj(json_response: dict[str, Any]) -> Optional[Movie]:
        return Movie(
            title=json_response.get('nameRu'),
            original_title=json_response.get('nameOriginal'),
            description=json_response.get('description'),
            poster=json_response.get('posterUrl'),
            id_kp=json_response.get('kinopoiskId'),
            id_imdb=json_response.get('imdbId'),
            rating_kp=json_response.get('ratingKinopoisk'),
            rating_imdb=json_response.get('ratingImdb')
        )
