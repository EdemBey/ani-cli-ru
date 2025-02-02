from typing import Any

from anicli_ru.base import *


class Anime(BaseAnimeHTTP):
    """API method write in snake_case style.
    For details see docs on https://github.com/anilibria/docs/blob/master/api_v2.md"""

    BASE_URL = "https://api.anilibria.tv/v2/"

    INSTANT_KEY_REPARSE = True
    _TESTS = {
        "search": ("Зомбиленд", 12),
        "ongoing": True,
        "search_blocked": False,
        "video": True,
        "search_not_found": "_thisTitleIsNotExist123456",
        "instant": "Зомбиленд"
    }

    def api_request(self, *, api_method: str, request_method: str = "GET", **kwargs) -> dict:
        """
        :param str api_method: Anilibria api method
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

    def search_titles(self, *, search: str, limit: int = -1, **kwargs) -> dict:
        """searchTitles method

        :param search:
        :param limit:
        :param kwargs:
        :return:
        """
        params = self._kwargs_pop_params(kwargs, search=search, limit=limit)
        return self.api_request(api_method="searchTitles", params=params, **kwargs)

    def get_updates(self, *, limit: int = -1, **kwargs) -> dict:
        """getUpdates method

        :param limit:
        :param kwargs:
        :return:
        """
        params = self._kwargs_pop_params(kwargs, limit=limit)
        return self.api_request(api_method="getUpdates", data=params, **kwargs)

    def episode_reparse(self, *args, **kwargs):
        raise NotImplementedError

    def get_anime(self, name):

        try:
            result =  self.search(name)[0]
            return EpisodeList.parse(result)
        except:
            return []
        
    def search(self, q: str) -> ResultList[BaseAnimeResult]:
        return AnimeResult.parse(self.search_titles(search=q))



class Player(BaseJsonParser, BasePlayer):
    url = ''
    quality: dict

    def __str__(self):
        return f"Серия {self.serie}"
    
    @classmethod
    def parse(cls, result: dict) -> ResultList:
        return[cls(**result)]
    
    def get_video(self, quality: int = 1080, *args, **kwargs) -> str:
        i = sorted(k for k in self.quality if k >= quality)
        return  self.quality[next(iter(i), max(self.quality, key=int))]


class Episode(BaseJsonParser):
    KEYS = ('serie', 'created_timestamp', 'preview', 'skips', 'hls', 'host')
    host: str  # not used in real API response
    serie: int
    created_timestamp: int
    preview: Any
    skips: dict
    hls: dict

    def __str__(self):
        return f"Episode {self.serie}"

    def player(self) -> ResultList[Player]:
        # {url: str, key: str}
        rez = {'quality': {}}
        for k, v in self.hls.items():
            if v:  # value maybe equal None
                url = self.host + v if self.host.startswith("http") else f"https://{self.host}{v}"
                k = {'fhd': 1080, 'hd': 720}.get(k, 480)
                rez['quality'][k] = url
                rez['serie'] = self.serie
        return Player.parse(rez)


class AnimeResult(BaseJsonParser):
    KEYS = ('id', 'code', 'names', 'status', 'announce', 'posters', 'updated', 'last_change', 'type',
            'genres', 'team', 'season', 'description', 'in_favorites', 'blocked', 'player', 'torrents')
    id: int
    code: str
    names: dict
    announce: Any
    status: dict
    posters: dict
    updated: int
    last_change: int
    type: dict
    genres: list
    team: dict
    season: dict
    description: str
    in_favorites: int
    blocked: dict
    player: dict
    torrents: dict

    def __str__(self):
        return self.names['ru']

    def episodes(self) -> ResultList[Episode]:
        host = self.player["host"]
        for p in self.player["playlist"].values():
            p["host"] = host
        playlist = list(self.player["playlist"].values())
        return Episode.parse(playlist)

class EpisodeList(BaseJsonParser, BaseEpisode):

    @classmethod
    def parse(cls, result:AnimeResult) -> ResultList[Episode]:
        return [cls(**{"names": result.names, "play":result.player})]
    
    def player(self)-> ResultList[Player]:
        anime = AnimeResult.parse({'player':self.play})[0]
        episodes = AnimeResult.episodes(anime)
        return sum((Episode.player(i) for i in episodes), [])

    def __str__(self):
        return f"Плеер AniLibria count: {self.play['series']['last']}"
    
class Ongoing(AnimeResult):
    # response equal AnimeResult object
    pass
