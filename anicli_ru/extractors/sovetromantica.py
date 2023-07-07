from __future__ import annotations
import re
from typing import Union

from anicli_ru.base import *


class Anime(BaseAnimeHTTP):
    BASE_URL = "https://service.sovetromantica.com/v1/"

    INSTANT_KEY_REPARSE = True

    def api_request(self, *, api_method: str, request_method: str = "GET", **kwargs) -> dict:
        """
        :param str api_method: Animevost api method
        :param str request_method: requests send method type. Default "GET"
        :param kwargs: any requests.Session kwargs
        :return: json response
        """
        resp = self.session.request(request_method, self.BASE_URL + api_method, **kwargs)
        return resp.json()

    @staticmethod
    def _kwargs_pop_params(kwargs, **params) -> dict:
        data = kwargs.pop("params") if kwargs.get("params") else {}
        data.update(params)
        return data

    def search_titles(self, search: str, **kwargs) -> dict:
        params = self._kwargs_pop_params(kwargs, anime_name=search)
        return self.api_request(api_method="animesearch",  params=params, **kwargs)

    def get_updates(self) -> dict:
        return self.api_request(api_method="ongoing")

    def episode_reparse(self, *args, **kwargs):
        raise NotImplementedError

    def search(self, q: str) -> ResultList[BaseAnimeResult]:
        return AnimeResult.parse(self.search_titles(search=q))


    def episodes(self, result: Union[AnimeResult, Ongoing], *args, **kwargs) -> ResultList[BaseEpisode]:  # type: ignore
        anime_id = result.anime_id
        path = "anime/{}/episodes".format(anime_id)
        req = self.api_request(api_method=path)
        return Episode.parse({"episodes": req})  # signature fix issue

    def players(self, *args, **kwargs) -> ResultList[BasePlayer]:
        raise NotImplementedError("Get this object from Episode object")

    def get_video(self, player_url: str, quality: int = 720, *, referer: str = ""):
        raise NotImplementedError("Get video from Player object")


class Player(BaseJsonParser):
    KEYS = ('key', 'url')
    key: str
    url: str

    def __str__(self):
        return self.key
    

    def get_video(self, *args, **kwargs):
        return self.url


class Episode(BaseJsonParser):
    ANIME_HTTP = Anime()
    KEYS = ('embed', 'episode_anime', 'episode_count', 'episode_id', 'episode_type', 'episode_view')
    embed: str
    episode_anime: int
    episode_count: int
    episode_id: int
    episode_type: int 
    episode_view: int


    def __str__(self):
        type = "Озвучка" if (self.episode_type) else "Субтитры"
        return "Серия {} - {}".format(self.episode_count, type)

    @classmethod
    def parse(cls, response) -> ResultList:
        """class object factory

        :param response: json response
        :return: ResultList with objects
        """

        rez = []
        if isinstance(response["episodes"], list):  # type: ignore
            for data in response["episodes"]:  # type: ignore
                c = cls()
                for k in data.keys():
                    if k in cls.KEYS:
                        setattr(c, k, data[k])
                rez.append(c)
            sorted_rez = sorted(rez, key=lambda x: x.episode_count)
        return sorted_rez

    def get_quality(self, input_string, host):
        pattern = r'RESOLUTION=\d+x(\d+)\n(.*?)\.m3u8'
        matches = re.findall(pattern, input_string)
        matches = sorted(matches, key=lambda x: int(x[0]), reverse=True)
        result = [{'key': match[0]+'p', 'url': '{}/{}.m3u8'.format(host, match[1])} for match in matches]
        return result
    
    def get_playlist(self, *args, **kwargs):
        with self.ANIME_HTTP as a:
            anime_data = a.session.request('GET', self.embed).text
            playlist = re.search(r'"file":"([^"]+)"', anime_data).group(1)
            host = playlist.rsplit('/', 1)[0]
            playlist_data = a.session.request('GET', playlist).text
            quality_list = self.get_quality(playlist_data, host)
            return quality_list
        
    def player(self) -> ResultList[Player]:
        rez = []
        playlist = self.get_playlist()
        rez.extend(Player.parse(playlist))
        return rez

class AnimeResult(BaseJsonParser):
    ANIME_HTTP = Anime()
    KEYS = ('anime_id', 'anime_description', 'anime_episodes', 'anime_folder', 'anime_keywords', 'anime_name', 
            'anime_name_russian', 'anime_paused', 'anime_shikimori', 'anime_studio', 'anime_year')
    anime_id: int
    anime_description: str
    anime_episodes: int
    anime_folder: str
    anime_keywords: str
    anime_name: str
    anime_name_russian: str
    anime_paused: int
    anime_shikimori: int
    anime_studio: int
    anime_year: int

    def __str__(self):
        return self.anime_name_russian

    def episodes(self):
        with self.ANIME_HTTP as a:
            return a.episodes(self)
        
    
class Ongoing(AnimeResult):
    # response equal AnimeResult object
    pass
