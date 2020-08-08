import requests
import os
from urllib.parse import urlparse

from html_telegraph_poster import TelegraphPoster
from newspaper import Article, Config as NewspaperConfig
from xml.etree import ElementTree

repo_url = 'https://github.com/Kylmakalle/tinkoff-journal-courses-unlocker'

conf = NewspaperConfig()
conf._language = 'ru'

course_url = input('Вставьте ссылку на курс: ')
course_url = course_url.rstrip().rstrip('/')

session = requests.sessions.Session()

# Getting course lesson
lessons_api_url = 'https://urania.tinkoffjournal.ru/api/v3/lessons'

lessons = session.get(lessons_api_url, params={'course_key': urlparse(course_url.rstrip('/')).path.rsplit("/", 1)[-1]},
                      verify=False)

# t.create_api_token('TelegraPyBot', '@TelegraPyBot', 'https://t.me/TelegraPyBot')['access_token']
tp = TelegraphPoster(access_token=os.environ.get('TELEGRA_PH_TOKEN', None))

for lesson in lessons.json()['data']:
    lesson_url = 'https://journal.tinkoff.ru/{}/'.format(lesson['slug'])

    if session.get(lesson_url).status_code == 200:

        article = Article(lesson_url, config=conf, keep_article_html=True)
        article.download()
        article.parse()
        if len(article.text) > 0:
            html = article.article_html
        else:
            html = str(ElementTree.tostring(article.clean_top_node), 'utf-8')

        post = tp.post(title=article.title,
                       author='Sergey Akentev via Tinkoff Journal Parser',
                       author_url=repo_url,
                       text='<img src="{}">'.format(
                           article.top_image) + html + '<br><br><a href="{}">Оригинал</a>'.format(
                           lesson_url))

        print(post['url'])

    else:
        print('Lesson', lesson_url, 'is unavailable yet')
