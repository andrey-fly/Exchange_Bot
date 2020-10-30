import os
import re
import sqlite3
import time
import logging
import requests
import threading
from bs4 import BeautifulSoup

logging.basicConfig(level=logging.INFO)


class RateProcessing:
    """
    Инициализация класса
    """

    def __init__(self, upd_time: int):

        self.currencies_ref_dict = {
            'EUR': 'https://www.google.com/search?ei=ijQkX56kHcGEwPAPtPSa2AQ&q=%D0%BA%D1%83%D1%80%D1%81+%D0%B5%D0%B2'
                   '%D1%80%D0%BE+%D0%BA+%D1%80%D1%83%D0%B1%D0%BB%D1%8E&oq=%D0%BA%D1%83%D1%80%D1%81+%D0%B5%D0%B2%D1%80'
                   '%D0%BE+%D0%BA+%D1%80%D1%83%D0%B1%D0%BB%D1%8E&gs_lcp=CgZwc3ktYWIQAzINCAAQsQMQgwEQRhCCAjIICAAQsQMQ'
                   'gwEyCAgAELEDEIMBMgYIABAHEB4yCAgAELEDEIMBMgYIABAHEB4yAggAMgIIADIGCAAQBxAeMgIIADoHCAAQsAMQQzoICAAQ'
                   'BxAKEB46BAgAEA1QhbERWPvWEWCe3hFoA3AAeACAAVaIAboGkgECMTOYAQCgAQGqAQdnd3Mtd2l6wAEB&sclient=psy-ab'
                   '&ved=0ahUKEwiekdiV4_fqAhVBAhAIHTS6BksQ4dUDCAw&uact=5',
            'USD': 'https://www.google.com/search?ei=fDQkX5esEsOxrgTI_ImADQ&q=%D0%BA%D1%83%D1%80%D1%81+%D0%B4%D0%BE%'
                   'D0%BB%D0%BB%D0%B0%D1%80%D0%B0+%D0%BA+%D1%80%D1%83%D0%B1%D0%BB%D1%8E&oq=%D0%BA%D1%83%D1%80%D1%81+'
                   '%D0%B4%D0%BE%D0%BB%D0%BB%D0%B0%D1%80%D0%B0+%D0%BA+%D1%80%D1%83%D0%B1%D0%BB%D1%8E&gs_lcp=CgZwc3k'
                   'tYWIQAzIPCAAQsQMQgwEQQxBGEIICMggIABCxAxCDATIICAAQsQMQgwEyBQgAELEDMgIIADICCAAyAggAMggIABCxAxCDATI'
                   'CCAAyAggAOgcIABCwAxBDOgoIABCxAxCDARBDOgQIABBDOgQIABAKOgkIABBDEEYQggI6BwgAELEDEENQsylYmWZglmhoBHAA'
                   'eACAAWOIAewJkgECMTmYAQCgAQGqAQdnd3Mtd2l6wAEB&sclient=psy-ab&ved=0ahUKEwiX2vaO4_fqAhXDmIsKHUh-AtA'
                   'Q4dUDCAw&uact=5',
            'CHF': 'https://www.google.com/search?ei=rTUkX4bmMMTnrgTnpKLADg&q=%D0%BA%D1%83%D1%80%D1%81+%D1%88%D0%'
                   'B2%D0%B5%D0%B9%D1%86%D0%B0%D1%80%D1%81%D0%BA%D0%BE%D0%B3%D0%BE+%D1%84%D1%80%D0%B0%D0%BD%D0%BA%'
                   'D0%B0+%D0%BA+%D1%80%D1%83%D0%B1%D0%BB%D1%8E&oq=%D0%BA%D1%83%D1%80%D1%81+%D1%88%D0%B2%D0%B5%D0%'
                   'B9%D1%86%D0%B0&gs_lcp=CgZwc3ktYWIQARgBMg0IABCxAxCDARBGEIICMgIIADICCAAyAggAMgIIADICCAAyAggAMgII'
                   'ADICCAAyAggAOgcIABCwAxBDOggIABCxAxCDAToFCAAQsQM6CggAELEDEIMBEEM6BAgAEEM6DwgAELEDEIMBEEMQRhCCA'
                   'lCkngNYg9QDYMLmA2gDcAB4AIABUIgBwQWSAQIxMZgBAKABAaoBB2d3cy13aXqwAQDAAQE&sclient=psy-ab',
            'BTC': 'https://www.google.com/search?ei=NcIqX8q4FIqwrgSz3K6ACg&q=bitcoin+to+rub&oq=bitcoin+to+&gs_lcp='
                   'CgZwc3ktYWIQARgBMg0IABCxAxCDARBGEIICMgIIADICCAAyAggAMgIIADICCAAyAggAMgIIADICCAAyAggAOggIABCxAxCD'
                   'AToFCAAQsQM6AgguOgUILhCxAzoJCAAQsQMQChABOgoIABCxAxCDARBDOgQIABBDOgcIABCxAxBDOgwIABCxAxBDEEYQggI6'
                   'CQgAEEMQRhCCAlCXLFiEggFguY8BaANwAHgAgAF9iAGgCJIBBDExLjKYAQCgAQGqAQdnd3Mtd2l6sAEAwAEB&sclient=psy-ab'
        }
        self.currency_rates_list = []
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/83.0.4103.106 Safari/537.36'
        }
        self.upd_time = upd_time

    def parse_html(self, key=None):
        # Функция парсинга страницы
        full_page = requests.get(self.currencies_ref_dict[key], headers=self.headers)
        soup = BeautifulSoup(full_page.content, 'html.parser')
        convert = soup.find_all('span', {'class': 'DFlfde SwHCTb', 'data-precision': 2})
        return str(convert[0])

    def normalize_rates(self, key=None):
        # Функция, приводящая значения валют к общему виду
        found_rate = re.findall(r'\d{,9}[.]\d{,5}', self.parse_html(key))
        return round(float(found_rate[0]), 2)

    def get_rate(self, key=None):
        return self.normalize_rates(key)

    def thread(self):
        conn = sqlite3.connect("currencies_db.db")
        cursor = conn.cursor()
        start_time = time.time() - self.upd_time
        while True:
            if (time.time() - start_time) < self.upd_time:
                continue
            else:
                start_time = time.time()
                db_exists = int(cursor.execute("""SELECT COUNT(name) 
                                                     FROM sqlite_master
                                                     WHERE type = 'table' 
                                                     AND name = 'updated_currencies'""").fetchone()[0])
                if db_exists:
                    for key in self.currencies_ref_dict:
                        cursor.execute('UPDATE updated_currencies SET curr_value = ?, '
                                       'time = ? WHERE curr_code = ?',
                                       (self.get_rate(key), time.time(), key))
                        conn.commit()
                else:
                    cursor.execute("""CREATE TABLE updated_currencies(
                                                                        curr_code VAR_CHAR(3),
                                                                        curr_value DECIMAL(10, 2),
                                                                        time INT(30)
                                                                        )""")
                    for key in self.currencies_ref_dict.keys():
                        cursor.execute('INSERT INTO updated_currencies VALUES (?, ?, ?)',
                                       (key, self.get_rate(key), time.time()))
                        conn.commit()
                logging.info('Курсы валют обновлены')

    def execute(self):
        threading.Thread(target=self.thread).start()
