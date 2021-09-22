from datetime import time
from flask import Flask
import requests
from bs4 import BeautifulSoup
import json
import base64
from middleware.config import headers
from playwright.sync_api import sync_playwright
from models.tables import serials, seazons, episodes, voices, CONNECTION
import time
from models.requests.voices import GetVoicesByVoice, InsertVoice



app = Flask(__name__)


@app.route('/', methods=['GET'])
def index():

    index_url = 'http://seasonvar.ru'

    response = requests.get(index_url, headers=headers)
    soup = BeautifulSoup(response.text, 'lxml')


    list_voices = soup.find_all('select', {'data-filter':"golosa"})[0].text # получаем список озвучек
    list_voices = list_voices.split('\n')
    list_voices.pop(0)
    list_voices.pop(0)
    list_voices.pop(-1)
    for voice in list_voices: # запись озвучек в базу
        if(not GetVoicesByVoice(voice)):
            InsertVoice(voice)

    urls = soup.find_all('div', class_='lside-serial')[0] # получаю список всех сериалов
    Parse(urls)

    return json.dumps({'data': 12})


def Parse(urls): # главный парсер
    for url in urls.findAll('a'):

        link = 'http://seasonvar.ru' + url.get('href') # ссылка на последний сезон сериала


        serial_name = url.text
        print(serial_name)
        # ==========Сериал==========
        #
        # serial_name -------- название сериала
        #
        # ==========Сериал==========


        single_page = PwSingle(link) # парсинг динамического контента на странице сезона

        list_seasons = single_page.select_one('ul.tabs-result')
        list_seasons = list_seasons.findAll('a') # список сезонов сериала


        SECURE_MARK = single_page.select_one('div.pgs-player')
        SECURE_MARK = SECURE_MARK.findAll('script')[1].text
        SECURE_MARK = SECURE_MARK[SECURE_MARK.find(":")+3 : SECURE_MARK.find("\',")] # получаем хэш для страниц

        SeasonParse(list_seasons, SECURE_MARK)
        


def PwSingle(link):
    with sync_playwright() as p:
        browser = p.firefox.launch()
        page = browser.new_page()
        page.goto(link, timeout = 0)
        single_page = BeautifulSoup(page.content(), 'lxml') # html код страницы сезона
        browser.close()
        return single_page



def SeasonParse(list_seasons, SECURE_MARK):
    for season_number, season in enumerate(list_seasons):
        season_number +=1

        season_link = 'http://seasonvar.ru' + season.get("href") # ссылка на каждый сезон сериала(с первого до последнего)

        res = requests.get(season_link, headers=headers)
        this_single_page = BeautifulSoup(res.text, 'lxml') # не динамический html текст страницы сезона

        season_description = this_single_page.select_one('p', {'itemprop':"description"}).text
        season_title = this_single_page.select_one('h1', {'itemprop':"name"}).text
        # ==========Сезон==========
        #
        # season_title -------- название сезона
        # season_description -- описание сезона
        # season_number ------- номер сезона
        # season_link --------- ссылка на сезон
        #
        # ==========Сезон==========

        seasonvar_season_id = this_single_page.select_one('div.pgs-sinfo').get('data-id-season')
        time.sleep(1)

        voices = ['','FOX','BaibaKo','RG.Paravozik','Субтитры','Hamster','Трейлеры', 'HDRezka']

        ParseVoices(voices, SECURE_MARK, seasonvar_season_id)
        time.sleep(1)


def ParseVoices(voices, SECURE_MARK, seasonvar_season_id):
    for voice in voices:
        voice_link = 'http://seasonvar.ru/playls2/{}/trans{}/{}/plist.txt'.format(SECURE_MARK, voice, seasonvar_season_id)

        response1 = requests.get(voice_link, headers=headers)
        media_voices = BeautifulSoup(response1.text, 'lxml').text
        media_voices = json.loads(media_voices)

        ParseSeries(media_voices)
        


def ParseSeries(media_voices):
    for series_number, media in enumerate(media_voices):
        series_number +=1
        series_url = media['file'] # хэшированый url медиа файлов || начинается на #2...//b2xvbG8=...
        series_url = series_url[2:series_url.find("//")] + series_url[series_url.find("=")+1:] # хэшированый url медиа файлов
        series_url = base64.b64decode(series_url).decode("UTF-8") # url серии
        print(series_url)
        series_title = media['title'] # название серии
        series_subtitle = media['subtitle'] # ссылка на субтитры к серии || начинается на [ru]http://...,[eng]http://...
        # ==========Серия==========
        #
        # series_title -------- название серии
        # voice --------------- озвучка
        # series_number ------- номер серии
        # series_url ---------- ссылка на серию
        #
        # ==========Серия==========


if __name__ == '__main__':
    app.run(debug=True)