"""
Parsing exchange rates and check currencies levels
"""
import re
import sqlite3
import time
import threading
import requests
from bs4 import BeautifulSoup


class RateProcessing:
    """
    Инициализация класса
    """

    def __init__(self, upd_time: int):

        self.currencies_ref_dict = {
            'EUR': 'https://www.google.com/search?ei=ijQkX56kHcGEwPAPtPSa2AQ&q='
                   '%D0%BA%D1%83%D1%80%D1%81+%D0%B5%D0%B2%D1%80%D0%BE+%D0%BA+%'
                   'D1%80%D1%83%D0%B1%D0%BB%D1%8E&oq=%D0%BA%D1%83%D1%80%D1%81+'
                   '%D0%B5%D0%B2%D1%80%D0%BE+%D0%BA+%D1%80%D1%83%D0%B1%D0%BB%'
                   'D1%8E&gs_lcp=CgZwc3ktYWIQAzINCAAQsQMQgwEQRhCCAjIICAAQsQMQ'
                   'gwEyCAgAELEDEIMBMgYIABAHEB4yCAgAELEDEIMBMgYIABAHEB4yAggAMg'
                   'IIADIGCAAQBxAeMgIIADoHCAAQsAMQQzoICAAQBxAKEB46BAgAEA1QhbER'
                   'WPvWEWCe3hFoA3AAeACAAVaIAboGkgECMTOYAQCgAQGqAQdnd3Mtd2l6wA'
                   'EB&sclient=psy-ab&ved=0ahUKEwiekdiV4_fqAhVBAhAIHTS6BksQ4dUDCAw&uact=5',
            'USD': 'https://www.google.com/search?ei=fDQkX5esEsOxrgTI_ImADQ&q='
                   '%D0%BA%D1%83%D1%80%D1%81+%D0%B4%D0%BE%D0%BB%D0%BB%D0%B0%D1%'
                   '80%D0%B0+%D0%BA+%D1%80%D1%83%D0%B1%D0%BB%D1%8E&oq=%D0%BA%D1'
                   '%83%D1%80%D1%81+%D0%B4%D0%BE%D0%BB%D0%BB%D0%B0%D1%80%D0%B0+'
                   '%D0%BA+%D1%80%D1%83%D0%B1%D0%BB%D1%8E&gs_lcp=CgZwc3ktYWIQAz'
                   'IPCAAQsQMQgwEQQxBGEIICMggIABCxAxCDATIICAAQsQMQgwEyBQgAELEDM'
                   'gIIADICCAAyAggAMggIABCxAxCDATICCAAyAggAOgcIABCwAxBDOgoIABCx'
                   'AxCDARBDOgQIABBDOgQIABAKOgkIABBDEEYQggI6BwgAELEDEENQsylYmWZ'
                   'glmhoBHAAeACAAWOIAewJkgECMTmYAQCgAQGqAQdnd3Mtd2l6wAEB&sclie'
                   'nt=psy-ab&ved=0ahUKEwiX2vaO4_fqAhXDmIsKHUh-AtAQ4dUDCAw&uact=5',
            'CHF': 'https://www.google.com/search?ei=rTUkX4bmMMTnrgTnpKLADg&q=%'
                   'D0%BA%D1%83%D1%80%D1%81+%D1%88%D0%B2%D0%B5%D0%B9%D1%86%D0%B0'
                   '%D1%80%D1%81%D0%BA%D0%BE%D0%B3%D0%BE+%D1%84%D1%80%D0%B0%D0%'
                   'BD%D0%BA%D0%B0+%D0%BA+%D1%80%D1%83%D0%B1%D0%BB%D1%8E&oq=%D0'
                   '%BA%D1%83%D1%80%D1%81+%D1%88%D0%B2%D0%B5%D0%B9%D1%86%D0%B0&'
                   'gs_lcp=CgZwc3ktYWIQARgBMg0IABCxAxCDARBGEIICMgIIADICCAAyAggA'
                   'MgIIADICCAAyAggAMgIIADICCAAyAggAOgcIABCwAxBDOggIABCxAxCDATo'
                   'FCAAQsQM6CggAELEDEIMBEEM6BAgAEEM6DwgAELEDEIMBEEMQRhCCAlCkng'
                   'NYg9QDYMLmA2gDcAB4AIABUIgBwQWSAQIxMZgBAKABAaoBB2d3cy13aXqw'
                   'AQDAAQE&sclient=psy-ab',
            'BTC': 'https://www.google.com/search?ei=NcIqX8q4FIqwrgSz3K6ACg&q='
                   'bitcoin+to+rub&oq=bitcoin+to+&gs_lcp=CgZwc3ktYWIQARgBMg0IA'
                   'BCxAxCDARBGEIICMgIIADICCAAyAggAMgIIADICCAAyAggAMgIIADICCAA'
                   'yAggAOggIABCxAxCDAToFCAAQsQM6AgguOgUILhCxAzoJCAAQsQMQChABO'
                   'goIABCxAxCDARBDOgQIABBDOgcIABCxAxBDOgwIABCxAxBDEEYQggI6CQg'
                   'AEEMQRhCCAlCXLFiEggFguY8BaANwAHgAgAF9iAGgCJIBBDExLjKYAQCgA'
                   'QGqAQdnd3Mtd2l6sAEAwAEB&sclient=psy-ab'
        }
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) '
                          'AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/83.0.4103.106 Safari/537.36'
        }
        self.upd_time = upd_time
        self.users_to_send = {}
        self.flag_upd_uts = False

    def __parse_html(self, key: str):
        """
        Функция парсинга страницы
        :param key: str
        :return: str
        """

        full_page = requests.get(self.currencies_ref_dict[key], headers=self.headers)
        soup = BeautifulSoup(full_page.content, 'html.parser')
        convert = soup.find_all('span', {'class': 'DFlfde SwHCTb', 'data-precision': 2})
        return str(convert[0])

    def __get_rate(self, key: str):
        """
        Функция, приводящая значения валют к общему виду
        :param key: str
        :return: float
        """

        found_rate = re.findall(r'\d{,9}[.]\d{,5}', self.__parse_html(key))
        return round(float(found_rate[0]), 2)

    @staticmethod
    def set_level(user_id: int, name: str, chat_id: int, key: str, level: float):
        """
        Setting currency level to check
        :param user_id: int
        :param name: str
        :param chat_id: int
        :param key: str
        :param level: float
        :return: None
        """
        conn = sqlite3.connect("currencies_db.db")
        cursor = conn.cursor()
        cursor.execute('INSERT INTO currencies_levels VALUES (?, ?, ?, ?, ?)',
                       (user_id, name, chat_id, key, level))
        conn.commit()

    def get_id_to_send(self, key: str):
        """
        Getting user's id which currency level is smaller than rate exchange
        :param key: str
        :return: None
        """
        conn = sqlite3.connect("currencies_db.db")
        cursor = conn.cursor()
        db_exists = int(cursor.execute("SELECT COUNT(name) "
                                       "FROM sqlite_master WHERE type = 'table' "
                                       "AND name = 'currencies_levels'").fetchone()[0])
        if not db_exists:
            cursor.execute("CREATE TABLE currencies_levels(user_id INTEGER(20), "
                           "name VAR_CHAR(20), chat_id INTEGER(20), curr_code "
                           "VAR_CHAR(3), curr_value DECIMAL(10, 2))")
        cursor.execute("SELECT user_id, name, chat_id, curr_code,curr_value "
                       "FROM currencies_levels WHERE curr_value >= (SELECT "
                       "curr_value FROM updated_currencies WHERE curr_code = ?) "
                       "AND curr_code = ?", (key, key))
        self.users_to_send[key] = list(set(item for item in cursor.fetchall()))
        for item in self.users_to_send[key]:
            cursor.execute("DELETE FROM currencies_levels WHERE user_id = ? AND "
                           "curr_code = ? AND curr_value = ?", (item[0], key, item[4]))
        conn.commit()

    @staticmethod
    def get_flw_cur(user_id: int):
        """
        Get user's currencies levels
        :param user_id: int
        :return: tuple
        """
        conn = sqlite3.connect("currencies_db.db")
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM currencies_levels WHERE user_id = ?', (user_id,))
        return cursor.fetchall()

    def thread(self):
        """
        Thread that get exchange rates and check currencies levels
        :return: None
        """
        conn = sqlite3.connect("currencies_db.db")
        cursor = conn.cursor()
        start_time = time.time() - self.upd_time
        while True:
            if (time.time() - start_time) < self.upd_time:
                continue
            start_time = time.time()
            db_exists = int(cursor.execute("SELECT COUNT(name) FROM sqlite_master "
                                           "WHERE type = 'table' AND "
                                           "name = 'updated_currencies'").fetchone()[0])
            if db_exists:
                for key in self.currencies_ref_dict:
                    cursor.execute('UPDATE updated_currencies SET curr_value = ?, '
                                   'time = ? WHERE curr_code = ?',
                                   (self.__get_rate(key), time.time(), key))
                    conn.commit()
            else:
                cursor.execute("""CREATE TABLE updated_currencies(curr_code VAR_CHAR(3),
                                                                    curr_value DECIMAL(10, 2),
                                                                    time INT(30)
                                                                    )""")
                for key in self.currencies_ref_dict:
                    cursor.execute('INSERT INTO updated_currencies VALUES (?, ?, ?)',
                                   (key, self.__get_rate(key), time.time()))
                    conn.commit()
            for key in self.currencies_ref_dict:
                self.get_id_to_send(key)
            self.flag_upd_uts = True

    def execute(self):
        """
        Run thread
        :return: None
        """
        threading.Thread(target=self.thread).start()
