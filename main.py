import time
import telebot
import requests
import re
from datetime import datetime
from bs4 import BeautifulSoup
from telebot import types


class RateProcessing:

    def __init__(self):
        self.currencies_ref_dict = {
            'EUR': 'https://www.google.com/search?ei=CHr2XtuzO6LprgTN0omIAg&q=euro&oq=%D1%83%D0%B3%D0%BA%D1%89'
                   '&gs_lcp=CgZwc3ktYWIQARgDMggIABAKEAEQKjIGCAAQChABMgYIABAKEAEyBggAEAoQATIGCAAQChABMgYIABAKEA'
                   'EyBggAEAoQATIGCAAQChABMgYIABAKEAEyBggAEAoQAToECAAQRzoHCAAQsQMQQzoFCAAQsQM6AggAOgQIABBDOgwI'
                   'ABCxAxBDEEYQggI6BQgAEIMBUOcaWO8_YLJbaAFwAXgAgAF7iAHzBZIBBDExLjGYAQCgAQGqAQdnd3Mtd2l6sAEA&'
                   'sclient=psy-ab',
            'USD': 'https://www.google.com/search?q=%D0%BA%D1%83%D1%80%D1%81+%D0%B4%D0%BE%D0%BB%D0%BB%D0%B0%D1'
                   '%80%D0%B0&oq=rehc&aqs=chrome.1.69i57j0l7.2693j0j8&sourceid=chrome&ie=UTF-8'
        }
        self.currencies_ref_dict_key = 'USD'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/83.0.4103.106 Safari/537.36'
        }
        self.rate = 0.0000
        self.round_rate = 0.00

    def get_currency_ref(self):
        return self.currencies_ref_dict[self.currencies_ref_dict_key]

    def parse_html(self):
        full_page = requests.get(self.get_currency_ref(), headers=self.headers)
        soup = BeautifulSoup(full_page.content, 'html.parser')
        convert = soup.find_all('span', {'class': 'DFlfde SwHCTb', 'data-precision': 2})
        return str(convert[0])

    def get_rates(self):
        found_rates = re.findall(r'\d{,2}[.,]\d{,5}', self.parse_html())
        self.rate = float(found_rates[0])
        self.round_rate = float(found_rates[1].replace(',', '.'))


class ExchangeBot:

    def __init__(self, rate_processing: RateProcessing):
        self.rates_class = rate_processing
        self.tg_token = '1152544884:AAEtSB-YpxGFgsWXcrTCIxrFe1PiJXYVpMo'
        self.bot = telebot.TeleBot(self.tg_token)
        self.currency_variety_dict = {
            "Евро": ["EUR", "€"],
            "евро": ["EUR", "€"],
            "Доллар": ["USD", "$"],
            "доллар": ["USD", "$"],
        }

    def welcome_user(self):
        @self.bot.message_handler(commands=['start'])
        def send_welcome(message):
            self.bot.send_message(message.chat.id,
                                  "Добро пожаловать, {}!\nЯ - ExchangeBot. Подскажу тебе актуальный курс доллара "
                                  "и евро на данный момент. Чуть позже у меня добавится возможность предупреждать "
                                  "тебя о достижении долларом "
                                  "или евро курса, который ты укажешь сам!".format(message.from_user.first_name))

            main_menu = types.ReplyKeyboardMarkup(row_width=1)
            item_btn1 = types.KeyboardButton('Узнать курсы валют')
            item_btn2 = types.KeyboardButton('Установить уровень валюты')
            main_menu.add(item_btn1, item_btn2)
            self.bot.send_message(message.chat.id, "Выберите нужную опцию:", reply_markup=main_menu)

    def help_user(self):
        @self.bot.message_handler(commands=['help'])
        def send_welcome(message):
            self.bot.reply_to(message, "Для получения актуального курса доллара напиши Привет")

    def process_user_request(self):
        pass

    def process_rate_exchange(self):
        @self.bot.message_handler(content_types=['text'])
        def get_text_messages(message):
            if message.text in list(self.currency_variety_dict.keys()):
                self.rates_class.currencies_ref_dict_key = self.currency_variety_dict[message.text][0]
                self.bot.send_message(message.from_user.id,
                                      "3 секунды, пожалуйста.", disable_web_page_preview=0, disable_notification=0)
                self.rates_class.get_rates()
                self.bot.send_message(message.from_user.id,
                                      "На {}\n1 {} = {} ₽".format(
                                          time.ctime(time.time()),
                                          self.currency_variety_dict[message.text][1],
                                          self.rates_class.round_rate)
                                      )
            else:
                self.bot.send_message(message.chat.id, "Я тебя не понимаю. Напиши /help.")

    def set_currency_level(self):
        pass

    def execute(self):
        self.welcome_user()
        self.help_user()
        self.process_rate_exchange()
        self.bot.polling()


def main():
    rate_processing = RateProcessing()
    exchange_bot = ExchangeBot(rate_processing)
    exchange_bot.execute()


if __name__ == '__main__':
    main()
