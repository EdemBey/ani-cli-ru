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

    def episode_reparse(self, *args, **kwargs):
        raise NotImplementedError

    def search(self, q: str) -> ResultList[BaseAnimeResult]:
        return AnimeResult.parse(self.search_titles(search=q))

    def episodes(self, result: Union[AnimeResult, Ongoing], *args, **kwargs) -> ResultList[BaseEpisode]:  # type: ignore
        anime_id = result.anime_id
        path = "anime/{}/episodes".format(anime_id)
        req = self.api_request(api_method=path)
        return Episode.parse(req)

    def players(self, episode: Episode) -> ResultList[Player]:  # type: ignore
        return Player.parse(episode.videos)
    
    # parsing m3u8 to get links of different quality
    def get_quality(self, input_string, host):
        pattern = r'RESOLUTION=\d+x(\d+)\n(.*?)\.m3u8'
        matches = re.findall(pattern, input_string)
        matches = sorted(matches, key=lambda x: int(x[0]), reverse=True)
        result = [{'quality': int(match[0]), 'url': '{}/{}.m3u8'.format(host, match[1])} for match in matches]
        return result
    
    def get_links(self, embed: str):
        data = self.session.get(embed).text
        playlist = re.search(r'"file":"([^"]+)"', data).group(1)
        host = playlist.rsplit('/', 1)[0]
        playlist_data = self.session.request('GET', playlist).text
        quality_list = self.get_quality(playlist_data, host)
        return quality_list
    


class Player( BaseJsonParser ):
    ANIME_HTTP = Anime()
    KEYS = ('embed', 'episode_type', 'episode_count')
    embed: str
    quality: int
    episode_count: int
    episode_type: int
    url: str

    def __str__(self):
        type = "Озвучка" if (self.episode_type) else "Субтитры"
        return "Серия {} - {}".format(self.episode_count, type)
    
    def get_video(self, quality: int = 1080, *args, **kwargs):
        with self.ANIME_HTTP as a:
            quality_list = a.get_links(self.embed)
            self.url = next((item['url'] for item in quality_list if item['quality'] == quality), None)
            return self.url
        

class Episode(BaseJsonParser, BaseEpisode):
    ANIME_HTTP = Anime()
    videos:list
    episode_type: str
    count: int

    @classmethod
    def parse(cls, list: list) -> ResultList:
        return [cls(**{'episode_type': str(i), 'count': len(group), 'videos': group})
                for i in range(2)
                    for group in [[item for item in list if item['episode_type'] == i]]]  # dub id  # dub name  # count videos


    def __str__(self):
        type = "Озвучка" if (self.episode_type) else "Субтитры"
        return "{} count: {}".format(type, self.count)


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
