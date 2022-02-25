#!/usr/bin/python3
"""Основной CLI скрипт"""

from __future__ import annotations

from random import sample
from string import ascii_letters
from os import system
from os import name as sys_name
from typing import Union

from . import import_extractor
from .utils.player_starter import run_player
from .utils.player_tools import is_aniboom
from .options import ALL_PARSERS, setup_arguments, get_agent


args = setup_arguments()

PLAYER = "mpv"
OS_HEADERS_COMMAND = "http-header-fields"


# load chosen extractor
extractor = "anicli_ru.extractors.{}".format(ALL_PARSERS.get(args.SOURCE))
API = import_extractor(extractor)
if not args.UPGRADE and not args.FORCE:
    print("Chosen source:", API.Anime.BASE_URL)


class Menu:
    def __init__(self):
        self.__ACTIONS = {"b": ("[b]ack next step", self.back_on),
                          "c": ("[c]lear console", self.cls),
                          "h": ("[h]elp", self.help),
                          "o": ("[o]ngoing print", self.ongoing),
                          "q": ("[q]uit", self.exit),
                          "e": ("[e]xit (alias quit)", self.exit),
                          }
        self.anime = API.Anime()
        if args.USERAGENT:
            self.anime.session.headers.update({"user-agent": args.USERAGENT})
        elif args.RANDOM_AGENT:
            agent = get_agent(args.RANDOM_AGENT_TYPE)
            if agent:
                self.anime.session.headers.update({"user-agent": agent})
        self.anime.TIMEOUT = args.TIMEOUT
        self.__back_action = True

    def back_on(self):
        self.__back_action = False

    def back_off(self):
        self.__back_action = True

    @property
    def is_back(self):
        return self.__back_action

    def command_wrapper(self, command) -> bool:
        self.cls()
        if self.__ACTIONS.get(command):
            self.__ACTIONS[command][1]()
            return True
        return False

    def ongoing(self):
        while self.is_back:
            ongoings = self.anime.ongoing()
            if len(ongoings) > 0:
                ongoings.print_enumerate()
                print("Choose anime:", 1, "-", len(ongoings))
                command = input(f"c_o [1-{len(ongoings)}] > ")
                if self.command_is_digit(command):
                    self.choose_episode(ongoings[int(command) - 1])
            else:
                print("Cannot grub ongoings, try running this script with the -s argument or use VPN or proxy")
                return
        self.back_off()

    def _run_video(self, player: API.Player):
        url = self.anime.get_video(player.url, args.QUALITY)
        if is_aniboom(url):
            if args.DOWNLOAD:
                self._download(
                    f'ffmpeg -y -headers "Referer: https://aniboom.one" -i "{url}" "{"".join(sample(ascii_letters, 12))}.mp4"')
            else:
                command_ = {OS_HEADERS_COMMAND: "Referer: https://aniboom.one"}
                run_player(url, **command_)
        elif args.DOWNLOAD:
            self._download(f'ffmpeg -y -i "{url}" "{"".join(sample(ascii_letters, 12))}.mp4"')
        else:
            run_player(url)

    def choose_dub(self, results: API.ResultList[API.Player]):
        while self.is_back:
            results.print_enumerate()
            print("Choose dub:", 1, "-", len(results))
            command = input(f"c_d [1-{len(results)}] > ")
            if self.command_is_digit(command):
                command = int(command)
                if command <= len(results):
                    print("Start playing")
                    if args.INSTANT:
                        for player in results[command - 1:]:
                            self._run_video(player)
                    else:
                        self._run_video(results[command - 1])
        self.back_off()

    def choose_episode(self, result: Union[API.AnimeResult, API.Ongoing]):
        episodes = result.episodes()
        if len(episodes) > 0:
            while self.is_back:
                episodes.print_enumerate()
                print(f"Choose episode: 1-{len(episodes)}")
                command = input(f"c_e [1-{len(episodes)}] > ")
                if self.command_is_digit(command):
                    command = int(command)
                    if command <= len(episodes):
                        results = episodes[command - 1].player()
                        if len(results) > 0:
                            self.choose_dub(results)
                        else:
                            print("No available dubs")
                            return
            self.back_off()
        else:
            print(
                "Episodes not found :(\nThis anime-title maybe blocked in your country, try using a vpn/proxy or change "
                "source with -s argument and repeat operation")
        return

    def choose_anime(self, results: API.ResultList[API.AnimeResult]):
        while self.is_back:
            results.print_enumerate()
            print("Choose anime:", 1, "-", len(results))
            command = input(f"c_a [1-{len(results)}] > ")
            if self.command_is_digit(command):
                command = int(command)
                if 0 < command <= len(results):
                    self.choose_episode(results[command - 1])
                return
        self.back_off()

    def find(self, pattern):
        results = self.anime.search(pattern)
        if len(results) > 0:
            print("Found", len(results))
            self.choose_anime(results)
        else:
            print("Not found!")
            return

    def main(self):
        if args.PROXY:
            self.proxy()
        while True:
            print("Input anime name or USAGE: h for get commands")
            command = input("m > ")
            if not self.command_wrapper(command):
                self.find(command)

    @staticmethod
    def cls():
        system("cls") if sys_name == 'nt' else system("clear")

    @staticmethod
    def _download(command: str):
        system(command)

    def proxy(self):
        print("Check proxy")
        try:
            self.anime.session.get(self.anime.BASE_URL, proxies=dict(http=args.PROXY, https=args.PROXY),
                                   timeout=10)
        except Exception as e:
            print(e.__class__.__name__, "Failed proxy connect")
            self.exit()
        self.anime.session.proxies.update(dict(http=args.PROXY, https=args.PROXY))
        print("Proxy connect success")

    def command_is_digit(self, command: str) -> bool:
        return not self.command_wrapper(command) and command.isdigit()

    @staticmethod
    def exit():
        exit(0)

    def help(self):
        for k, v in self.__ACTIONS.items():
            print(k, v[0])

    @classmethod
    def run(cls):
        cls().main()


def main():
    try:
        Menu.run()
    except KeyboardInterrupt:
        print("KeyboardInterrupt, Exit...")
        exit(1)


if __name__ == '__main__':
    main()