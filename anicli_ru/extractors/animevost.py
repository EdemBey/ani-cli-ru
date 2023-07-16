from __future__ import annotations
from typing import Union
import json

from anicli_ru.base import *


class Anime(BaseAnimeHTTP):
    BASE_URL = "https://api.animevost.org/v1/"

    INSTANT_KEY_REPARSE = True

    def api_request(self, *, api_method: str, request_method: str = "GET", **kwargs) -> dict:
        """
        :param str api_method: Animevost api method
        :param str request_method: requests send method type. Default "POST"
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
        params = self._kwargs_pop_params(kwargs, name=search)
        return self.api_request(api_method="search", request_method="POST", data=params, **kwargs)['data']

    def get_updates(self, *, limit: int = 20, **kwargs) -> dict:
        params = self._kwargs_pop_params(kwargs, page=1, quantity=limit)
        return self.api_request(api_method="last", params=params, **kwargs)['data']

    def episode_reparse(self, *args, **kwargs):
        raise NotImplementedError

    def search(self, q: str) -> ResultList[BaseAnimeResult]:
        return AnimeResult.parse(self.search_titles(search=q))

    def ongoing(self, *args, **kwargs) -> ResultList[BaseOngoing]:
        return Ongoing.parse(self.get_updates())

    def episodes(self, result: Union[AnimeResult, Ongoing], *args, **kwargs) -> ResultList[BaseEpisode]:  # type: ignore
        return Episode.parse(result.series)  # signature fix issue

    def players(self,result: Episode, *args, **kwargs) -> ResultList[BasePlayer]:
        res = {'quality': {}}
        host = 'https://fhd.trn.su/'
        mp4 = str(result.episode_id)+'.mp4'  
        sd = 'https://static.trn.su/'
        req = self.session.get(host+mp4)
        res['quality'] = {480: sd+mp4} if req.status_code == 404 else {1080: f"{host}1080/{mp4}", 720: f"{host}720/{mp4}", 480: host+mp4}
        return Player.parse(res)

    def get_video(self, player_url: str, quality: int = 720, *, referer: str = ""):
        raise NotImplementedError("Get video from Player object")


class Player(BaseJsonParser, BasePlayer):
    url = ''
    quality: dict

    def __str__(self):
        return self.key

    @classmethod
    def parse(cls, result: dict) -> ResultList:
        return[cls(**result)]
    
    def get_video(self, quality: int = 1080, *args, **kwargs) -> str:
        i = sorted(k for k in self.quality if k >= quality)
        return  self.quality[next(iter(i), max(self.quality, key=int))]


class Episode(BaseJsonParser, BaseEpisode):
    ANIME_HTTP = Anime()
    KEYS = ('std', 'preview', 'name', 'hd')
    name: str
    episode_id: str

    @staticmethod
    def sorting_series(sort_series):
        replace = sort_series.replace("\'", "\"")
        items = json.loads(replace).items()
        return list(items)

    def __str__(self):
        return self.name

    @classmethod
    def parse(cls, series) -> ResultList:
        episodes_list = cls.sorting_series(series)
        req = [cls(**{'name': k, 'episode_id': v}) for k, v in episodes_list]
        return req

 


class AnimeResult(BaseJsonParser):
    ANIME_HTTP = Anime()
    KEYS = ('id', 'description', 'isFavorite', 'rating', 'series', 'director', 'urlImagePreview', 'year',
            'genre', 'votes', 'title', 'timer', 'type', 'isLikes', 'screenImage')
    id: int
    description: str
    isFavorite: int
    rating: int
    series: dict
    director: str
    urlImagePreview: str
    year: str
    genre: str
    votes: int
    title: str
    timer: int
    type: str
    isLikes: int
    screenImage: list

    def __str__(self):
        return self.title

    def episodes(self):
        with self.ANIME_HTTP as a:
            return a.episodes(self)


class Ongoing(AnimeResult):
    # response equal AnimeResult object
    pass
