import time
import telebot
import requests
import re
from bs4 import BeautifulSoup
import threading


class RateProcessing:

    def __init__(self, dict_key=None):
        self.currencies_ref_dict = {
            'EUR': 'https://www.google.com/search?ei=CHr2XtuzO6LprgTN0omIAg&q=euro&oq=%D1%83%D0%B3%D0%BA%D1%89'
                   '&gs_lcp=CgZwc3ktYWIQARgDMggIABAKEAEQKjIGCAAQChABMgYIABAKEAEyBggAEAoQATIGCAAQChABMgYIABAKEA'
                   'EyBggAEAoQATIGCAAQChABMgYIABAKEAEyBggAEAoQAToECAAQRzoHCAAQsQMQQzoFCAAQsQM6AggAOgQIABBDOgwI'
                   'ABCxAxBDEEYQggI6BQgAEIMBUOcaWO8_YLJbaAFwAXgAgAF7iAHzBZIBBDExLjGYAQCgAQGqAQdnd3Mtd2l6sAEA&'
                   'sclient=psy-ab',
            'USD': 'https://www.google.com/search?q=%D0%BA%D1%83%D1%80%D1%81+%D0%B4%D0%BE%D0%BB%D0%BB%D0%B0%D1'
                   '%80%D0%B0&oq=rehc&aqs=chrome.1.69i57j0l7.2693j0j8&sourceid=chrome&ie=UTF-8'
        }
        self.currencies_ref_dict_key = dict_key
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


class CurrencyLevel:

    def __init__(self, dict_key, level=0.00):
        self.my_level = level
        self.currency_level = 0.0000
        self.rate_processing = RateProcessing(dict_key)
        self.currency_dict_key = dict_key
        self.flag_on = True

    def result_comparison(self):
        self.rate_processing.get_rates()
        self.rate_processing.currencies_ref_dict_key = self.currency_dict_key
        # if self.rate_processing.rate < self.my_level:
        #     return True
        # else:
        #     return False
        print(self.rate_processing.rate, self.my_level)

    def execute(self):
        while self.flag_on:
            self.result_comparison()
            time.sleep(5)

    # def unexecute(self):
    #     self.flag_on = False


class ExchangeBot:

    def __init__(self, rate_processing: RateProcessing):
        self.rates_class = rate_processing
        self.tg_token = '1152544884:AAH-x7Gzd4RcX7sgOPLHKm1wV7OFxJ1YgPY'
        self.menu = None
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
            self.show_main_menu(message)

    def show_main_menu(self, message):
        self.button_menu(('Узнать курс валюты', 'Установить уровень валюты'))
        self.bot.send_message(message.chat.id, "Выберите нужную опцию:", reply_markup=self.menu)
        self.show_button_menu()

    def show_button_menu(self):
        @self.bot.message_handler(content_types=['text'])
        def button_menu(message):
            if message.text == 'Узнать курс валюты':
                self.button_menu(('Евро', 'Доллар', 'Назад'))
                self.bot.send_message(message.chat.id, "Выберите нужную валюту:", reply_markup=self.menu)
                self.bot.register_next_step_handler(message, self.process_rate_exchange)
            elif message.text == 'Установить уровень валюты':
                self.button_menu(('Евро', 'Доллар', 'Назад'))
                self.bot.send_message(message.chat.id, "Выберите нужную валюту:", reply_markup=self.menu)
                self.bot.register_next_step_handler(message, self.process_rate_exchange)
            else:
                self.bot.send_message(message.chat.id, "Я тебя не понимаю, повтори запрос.")
                self.show_button_menu()

    def button_menu(self, params):
        self.menu = telebot.types.ReplyKeyboardMarkup()
        for item in params:
            self.menu.add(item)

    def help_user(self):
        @self.bot.message_handler(commands=['help'])
        def send_help(message):
            self.bot.reply_to(message, "Для получения актуального курса доллара напиши Привет")

    def process_user_request(self):
        pass

    def process_rate_exchange(self, message):
        if message.text in list(self.currency_variety_dict.keys()):
            self.rates_class.currencies_ref_dict_key = self.currency_variety_dict[message.text][0]
            self.bot.send_message(message.from_user.id,
                                  "Идет обработка запроса....")
            self.rates_class.get_rates()
            self.bot.send_message(message.from_user.id,
                                  "На {}\n1 {} = {:.2f} ₽".format(
                                      time.ctime(),
                                      self.currency_variety_dict[message.text][1],
                                      self.rates_class.round_rate)
                                  )
            self.bot.register_next_step_handler(message, self.process_rate_exchange)
        elif message.text == 'Назад':
            self.show_main_menu(message)
        else:
            self.bot.send_message(message.chat.id, "Я тебя не понимаю. Напиши /help.")
            self.bot.register_next_step_handler(message, self.process_rate_exchange)

    def process_currency_level(self, message):
        if message.text in list(self.currency_variety_dict.keys()):
            self.rates_class.currencies_ref_dict_key = self.currency_variety_dict[message.text][0]
            self.show_currency_level_menu()

    def show_currency_level_menu(self):
        pass

    # def set_currency_level(self, message):
    #
    #     my_level_usd = 71.15
    #     self.rates_class.currencies_ref_dict_key = 'USD'
    #     self.rates_class.get_rates()
    #     print('Программа запущена')
    #     print(self.rates_class.rate)
    #     if self.rates_class.rate < my_level_usd:
    #         self.bot.send_message(message.chat.id, "Бакс упал")
    #     self.button_menu(('Узнать курс валюты', 'Установить уровень валюты'))
    #     self.show_button_menu()
    #     time.sleep(10)
    #     self.set_currency_level(message)

    def execute(self):
        self.welcome_user()
        self.help_user()
        self.bot.infinity_polling(True)


def main():
    threads = [('EUR', 85.18), ('USD', 75.18)]
    for thread in threads:
        x = threading.Thread(target=CurrencyLevel(thread[0], thread[1]).execute, args=())
        x.start()

    exchange_bot = ExchangeBot(RateProcessing())
    exchange_bot.execute()


if __name__ == '__main__':
    main()
