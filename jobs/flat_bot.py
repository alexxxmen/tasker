# -*- coding:utf-8 -*-

import time
import datetime

import requests
from bs4 import BeautifulSoup as Soup

from jobs import _Job
from jobs.dao import models

from jobs.jobs_config import TELEGRAM_ID, TELEGRAM_BOT_TOKEN, TELEGRAM_BOT_URL
from controllers.send_message import SendMessageController


class FlatBotJob(_Job):
    def _execute(self, **kwargs):
        required_attrs = ("float_price_from", "float_price_to", "float_number_of_rooms_to",
                          "private_business", "district_id")
        for attr in required_attrs:
            if attr not in kwargs:
                self.log.debug('Missed "%s" argument in "%s"' % (attr, kwargs))
                raise Exception('Missed "%s" argument in "%s"' % (attr, kwargs))

        url = 'http://olx.ua/nedvizhimost/arenda-kvartir/dolgosrochnaya-arenda-kvartir/kiev/?' \
              'search[filter_float_price:from]=%s&search[filter_float_price:to]=%s&search' \
              '[filter_float_number_of_rooms:to]=%s&search[private_business]=%s&search[district_id]=%s' % \
              (kwargs["float_price_from"], kwargs["float_price_to"], kwargs["float_number_of_rooms_to"],
               kwargs["private_business"], kwargs["district_id"])
        send_message = SendMessageController(TELEGRAM_BOT_TOKEN)
        response = None
        try:
            response = requests.get(url)
        except Exception as e:
            self.log.exception('Exception during send request to url=%s' % url)
            send_message.call(TELEGRAM_BOT_URL, TELEGRAM_ID, e)

        if response.status_code != 200:
            self.log.debug('Unexpected response code=%s' % response.status_code)
            send_message.call(TELEGRAM_BOT_URL, TELEGRAM_ID, 'Unexpected response code=%s' % response.status_code)
            raise Exception('Unexpected response code=%s' % response.status_code)

        result = Soup(response.text, 'html.parser')

        offer_list = result.find_all('td', 'offer')
        if not offer_list:
            self.log.debug('Found 0 offers')
            raise Exception('Found 0 offers')
        if not models.Flat.table_exists():
            models.Flat.create_table()

        for offer in offer_list:
            url = offer.find_all('div', 'space rel')[0].h3.a['href']
            if url.find("#") != -1:
                url = url[:url.find("#")]

            if not models.Flat.select().where(models.Flat.url == url):
                time.sleep(0.2)
                # выбираем предложения только по опр району
                district_full = offer.find('p', 'color-9 lheight16 marginbott5').small.span.text.strip()
                if len(district_full.split(' ')) <= 1:
                    continue
                district = district_full.split(' ')[1]
                offer_dist_id = 0
                for d in kiev_districts:
                    if d.name == district:
                        offer_dist_id = d.id
                        break
                    else:
                        offer_dist_id = 0
                if offer_dist_id != kwargs["district_id"]:
                    continue

                title = offer.find_all('div', 'space rel')[0].h3.a.strong.text
                price = offer.find('p', 'price').strong.text
                date = offer.find('p', 'color-9 lheight16 marginbott5 x-normal').text
                date = self._prepare_date(date)
                self.log.debug('Start insert to db flat: title=%s, price=%s, offer_date=%s, url=%s' %
                               (title, price, date, url))
                models.Flat.create(
                    url=url,
                    title=title,
                    price=price,
                    offer_datetime=date
                )
                self.log.debug('Insert finished successful')
                telegram_text = u'Новое объявление\n%s\nЦена(%s) Дата добавления(%s)\nТекущая дата(%s)Ссылка(%s)' % \
                                (title, price, date, datetime.datetime.now(), url)
                send_message.call(TELEGRAM_BOT_URL, TELEGRAM_ID, telegram_text)

    def _prepare_date(self, date):
        parsed_date = date.split()
        return ' '.join(parsed_date)


class District(object):
    def __init__(self, name, dist_id):
        self.name = name
        self.id = dist_id

kiev_districts = [
    District(u'Голосеевский', 1),
    District(u'Дарницкий', 3),
    District(u'Деснянский', 5),
    District(u'Днепровский', 7),
    District(u'Оболонский', 9),
    District(u'Печерский', 11),
    District(u'Подольский', 13),
    District(u'Святошинский', 15),
    District(u'Соломенский', 17),
    District(u'Шевченковский', 19),
]
