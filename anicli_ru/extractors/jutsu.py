from __future__ import annotations
from typing import Union, List
from anicli_ru.base import *
import re


class Anime(BaseAnimeHTTP):
    BASE_URL = "https://jut.su"
    INSTANT_KEY_REPARSE = True
    SEARCH_URL = 'https://yandex.ru/search/site/'

    def search(self, q: str) -> ResultList[AnimeResult]:  # type: ignore
        text = '{} -episode -anime'.format(q)
        resp = self.session.get(f"{self.SEARCH_URL}", params={"searchid": 1893616, 
                                                              "url": self.BASE_URL,
                                                              "text":  text}).text
        return AnimeResult.parse(resp)

    def ongoing(self) -> ResultList[Ongoing]:  # type: ignore
        return "No function"



    def episodes(self, result: Union[AnimeResult, Ongoing]) -> ResultList[Episode]:  # type: ignore
        resp = self.session.get(result.url).text
        return Episode.parse(resp)

    def players(self, episode: Episode) -> ResultList[Player]:  # type: ignore
        resp = self.session.get(self.BASE_URL+episode.url).text
        return Player.parse(resp)
    
    def get_video(self, player_url: str, quality: int = 720, *, referer: str = ""):
        raise NotImplementedError("Get video from Player object")

class AnimeResult(BaseAnimeResult):
    REGEX = {"url": re.compile(r'<a\s+class="b-serp-item__title-link"\s+href="([^"]+)"'),
             "title": re.compile(r'<h3\s+class="b-serp-item__title"[^>]*>\s*<a[^>]*>\s*<span>(.*?)</span>\s*</a>\s*</h3>'),
            #  "type": re.compile(r'type/(.*?)">')
             }
    ANIME_HTTP = Anime()
    url: str
    title: str

    def __str__(self):
        return f"{self.title}"


class Episode(BaseEpisode):
    ANIME_HTTP = Anime()
    REGEX = {
             "name": re.compile(r'class="[^"]*\bvideo the_hildi\b[^"]*"><i>[^<]*</i>([^<]*)'),
             "url": re.compile(r'href="([^"]+)"\s+class="[^"]*\bvideo the_hildi\b[^"]*"')
             }
    name: str
    url: str
    def __str__(self):
        return f"{self.name}"


class Player(BasePlayer):
    REGEX = {
        "url": re.compile(r'<source[^>]+src="([^"]+)"'),
        "key": re.compile(r'<source[^>]+label="([^"]+)"')
    }
    key: str
    url = ''

   

    def get_video(self, *args, **kwargs):
        return self.url
    
    def __str__(self):
         return self.key

class Ongoing(AnimeResult):
    # response equal AnimeResult object
    pass