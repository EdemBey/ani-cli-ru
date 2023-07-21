
from anicli_ru.extractors import sovetromantica, animania, anilibria, animevost
from anicli_ru.base import *
import re



class Anime(BaseAnimeHTTP):
    BASE_URL = "https://animania.online"
    Animania = animania.Anime()
    Sovetromantica = sovetromantica.Anime()
    Anilibria = anilibria.Anime()
    Animevost = animevost.Anime()

    def episode_reparse(self, *args, **kwargs):
        # use this method if episodes come first,
        # and then the choice of dubs for the correct operation of the TUI app
        raise NotImplementedError

    def search(self, q: str) -> ResultList[BaseAnimeResult]:

        # Entrypoint for searching anime title by string query

        a = self.Animania.search(q)
        # return a
        return AnimeResult.parse(a)

    # def ongoing(self, *args, **kwargs) -> ResultList[BaseOngoing]:
    #     # Entrypoint for searching ongoings"""
    #     r = self.session.get(self.BASE_URL).text
    #     return Ongoing.parse(r)

    def episodes(self, result: BaseAnimeResult):
        sovetromantica_anime = self.Sovetromantica.get_anime(result.title)

        result_animania = self.Animania.episodes(result)
        result_anilibria = self.Anilibria.get_anime(result.title)
        result_animevost = self.Animevost.get_anime(sovetromantica_anime)
        result_sovetromantica = sovetromantica_anime.episodes()

        return result_animevost + result_anilibria + result_sovetromantica + result_animania

    # def players(self, *args, **kwargs) -> ResultList[BasePlayer]:
    #     # Entryponint for get video player url
    #     # If the source does not need to send HTTP request, do not override this, but call from the object Episode

    #     r = self.session.get(self.BASE_URL).text
    #     return Player.parse(r)


class AnimeResult(BaseAnimeResult):
    ANIME_HTTP = Anime()
    # REGEX = {"url": re.compile("foo (.*?)"),
    #          "title": re.compile("bar (.*?)")}

    url: str
    title: str

    def __str__(self):
        # return output in terminal or str() func
        return f"{self.title}"
    
    @classmethod
    def parse(cls, list) -> ResultList:
        res = []
        for item in list:
            x = cls(**{"url":item.url,"title": item.title})
            res.append(x)
        return res

class Ongoing(BaseOngoing):
    ANIME_HTTP = Anime()

    def __str__(self):
        return


class Player(BasePlayer):
    ANIME_HTTP = Anime()
    REGEX = {"url": re.compile("url (.*?)")}
    url: str

    def __str__(self):
        return


class Episode(BaseEpisode):
    ANIME_HTTP = Anime()

 
    @classmethod
    def parse(cls, list_a, list_s) -> ResultList:
        res = []
        for item in list_a:
            x = cls(**{"url":item.url,"title": item.title})
            res.append(x)
        return res
    

    def __str__(self):
        return ""
