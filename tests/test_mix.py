import sys
import os
path = os.path.abspath(".")
sys.path.append(path)


# quick example


from anicli_ru.extractors.mixed import *
from anicli_ru.loader import all_extractors

print(all_extractors())  # вывод всех доступных парсеров из директории extractors
a = Anime()
results = a.search("Магическая битва 2")  # поиск тайтла по названию
episodes = results[0].episodes()    # получить эпизоды с первого найденного тайтла
players = episodes[1].player()  # получить сырые ссылки на видеохостниги (не прямую ссылку на видео)
video = players[0].get_video(quality=480)  # получить прямую ссылку на видео с видеохостинга для плеера
print(video)