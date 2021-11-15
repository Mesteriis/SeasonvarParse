from datetime import time
import requests
from bs4 import BeautifulSoup
import json
import base64
from middleware.config import headers
from playwright.sync_api import sync_playwright
import time
from models.requests.serials import GetSerialsByTitle, InsertSerial
from models.requests.voices import GetVoicesByVoice, InsertVoice, GetAllVoices
from models.requests.seazons import GetSeazonByTitle_SerialId, InsertSeazon
from models.requests.episodes import InsertEpisode, GetEpisodeByLink
import logging

logging.basicConfig(filename='app.log', filemode="w",format='%(message)s, %(asctime)s', datefmt='%d-%b-%y %H:%M:%S')
start_time = time.time()

# count_serials_parse = int(input("Введите колличество сериалов которые спарсятся (0-если все): "))
start_serials_parse = int(input("Введите с какого сериала начать (1-n): "))


def index():

    index_url = 'http://seasonvar.ru'

    response = requests.get(index_url)
    soup = BeautifulSoup(response.text, 'lxml')

    # list_voices = soup.find_all('select', {'data-filter':"golosa"})[0].text # получаем список озвучек
    # list_voices = list_voices.split('\n')
    # list_voices.pop(1)
    # list_voices.pop()

    # for voice in list_voices: # запись озвучек в базу
    #     if(not GetVoicesByVoice(voice)):
    #         InsertVoice(voice)

    # получаю список всех сериалов
    urls = soup.find_all('div', class_='lside-serial')[0]

    Parse(urls)

    return json.dumps({'data': 12})



def Parse(urls):  # главный парсер
    for serial_count, url in enumerate(urls.findAll('a')):
        
        serial_count+=1
        if serial_count < start_serials_parse:
            continue
        # ссылка на последний сезон сериала
        link = 'http://seasonvar.ru' + url.get('href')
        serial_name = url.text

        serial = GetSerialsByTitle(serial_name)
        if(serial):
            serialId = serial[0].id
        else:
            serialId = InsertSerial(serial_name)

        # парсинг динамического контента на странице сезона
        single_page = PwSingle(link)

        list_seasons = single_page.select_one('ul.tabs-result')
        list_seasons = list_seasons.findAll('a')  # список сезонов сериала

        SECURE_MARK = single_page.select_one('div.pgs-player')
        SECURE_MARK = SECURE_MARK.findAll('script')[1].text
        SECURE_MARK = SECURE_MARK[SECURE_MARK.find(
            ":")+3: SECURE_MARK.find("\',")]  # получаем хэш для страниц


        logging.warning(f'#{serial_count} - {serial_name}')

        SeasonParse(serialId, list_seasons, SECURE_MARK)

        print(f'#{serial_count}-----{serial_name}-----{round(time.time() - start_time)} sec')

        # if ((count_serials_parse > 0) & (count_serials_parse == serial_count)):
        #     break


def PwSingle(link):
    with sync_playwright() as p:
        browser = p.firefox.launch()
        page = browser.new_page()
        page.goto(link, timeout=0)
        # html код страницы сезона
        single_page = BeautifulSoup(page.content(), 'lxml')
        browser.close()
        return single_page


def SeasonParse(serialId, list_seasons, SECURE_MARK):
    for season_number, season in enumerate(list_seasons):
        season_number += 1
        
        # ссылка на каждый сезон сериала(с первого до последнего)
        season_link = 'http://seasonvar.ru' + season.get("href")

        res = requests.get(season_link)
        # не динамический html текст страницы сезона
        this_single_page = BeautifulSoup(res.text, 'lxml')

        season_description = this_single_page.select_one(
            'p', {'itemprop': "description"}).text
        season_title = this_single_page.select_one(
            'h1', {'itemprop': "name"}).text
        season_img = this_single_page.select_one(
            'img', {'itemprop': "thumbnailUrl"}).get("src")
        season = GetSeazonByTitle_SerialId(season_title, serialId)
        if(season):
            seasonId = season[0].id
        else:
            seasonId = InsertSeazon(
                season_title, season_description, season_number, serialId, season_link, season_img)

        seasonvar_season_id = this_single_page.select_one(
            'div.pgs-sinfo').get('data-id-season')
        time.sleep(1)

        
        ParseVoices(seasonId, SECURE_MARK, seasonvar_season_id)
        time.sleep(1)
    logging.warning(f'\tКолличество сезонов={len(list_seasons)}-----Время парсинга={round(time.time() - start_time)} sec')
    # file_log.write(f'Колличество сезонов={len(list_seasons)}-----Время парсинга={round(time.time() - start_time)} sec\n')


def ParseVoices(seasonId, SECURE_MARK, seasonvar_season_id):
    voices = GetAllVoices()
    for voice in voices:
        voice_link = 'http://seasonvar.ru/playls2/{}/trans{}/{}/plist.txt'.format(
            SECURE_MARK, voice[1], seasonvar_season_id)
        response1 = requests.get(voice_link)
        media_voices = BeautifulSoup(response1.text, 'lxml').text
        media_voices = json.loads(media_voices)
        if(not len(media_voices)):
            continue
        else:
            ParseSeries(voice[0], media_voices, seasonId)


def ParseSeries(voiceId, media_voices, seasonId):
    for series_number, media in enumerate(media_voices):
        if('folder' in media):
            for series_folder, media_folder in enumerate(media['folder']):
                series_folder = (series_folder+1) * series_number
                SetEpisodes(media_folder, series_folder, seasonId, voiceId)
        else:
            series_number += 1
            SetEpisodes(media, series_number, seasonId, voiceId)


def SetEpisodes(media, series_number, seasonId, voiceId):
    # хэшированый url медиа файлов || начинается на #2...//b2xvbG8=...
    series_url = media['file']
    series_url = series_url.replace('//b2xvbG8=', '')
    series_url = series_url[2:] # хэшированый url медиа файлов
    series_url = base64.b64decode(series_url).decode("UTF-8")  # url серии

    series_title = media['title']  # название серии
    # ссылка на субтитры к серии || начинается на [ru]http://...,[eng]http://...
    series_subtitle = media['subtitle']

    episode = GetEpisodeByLink(series_url)
    if(episode):
        return
    else:
        InsertEpisode(series_title, voiceId, series_number,
                      seasonId, series_url, series_subtitle)


if __name__ == '__main__':
    index()