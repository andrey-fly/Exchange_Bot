import telebot
import requests
import re
from bs4 import BeautifulSoup
from telebot import types

TG_TOKEN = '1152544884:AAEtSB-YpxGFgsWXcrTCIxrFe1PiJXYVpMo'


class RateProcessing:

    def __init__(self):
        self.dollar_ruble_ref = 'https://www.google.com/search?q=%D0%BA%D1%83%D1%80%D1%81+%D0%B4%D0%BE%D0%BB%D0%BB%' \
                                'D0%B0%D1%80%D0%B0&oq=rehc&aqs=chrome.1.69i57j0l7.2693j0j8&sourceid=chrome&ie=UTF-8'
        self.euro_ruble_ref = 'https://www.google.com/search?ei=CHr2XtuzO6LprgTN0omIAg&q=euro&oq=%D1%83%D0%B3%D0%BA%' \
                              'D1%89&gs_lcp=CgZwc3ktYWIQARgDMggIABAKEAEQKjIGCAAQChABMgYIABAKEAEyBggAEAoQATIGCAAQChAB' \
                              'MgYIABAKEAEyBggAEAoQATIGCAAQChABMgYIABAKEAEyBggAEAoQAToECAAQRzoHCAAQsQMQQzoFCAAQsQM6A' \
                              'ggAOgQIABBDOgwIABCxAxBDEEYQggI6BQgAEIMBUOcaWO8_YLJbaAFwAXgAgAF7iAHzBZIBBDExLjGYAQCgA' \
                              'QGqAQdnd3Mtd2l6sAEA&sclient=psy-ab'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) '
                          'Chrome/83.0.4103.106 Safari/537.36'
        }
        self.rate = 0.0000
        self.round_rate = 0.00

    def parse_html(self):
        full_page = requests.get(self.dollar_ruble_ref, headers=self.headers)
        soup = BeautifulSoup(full_page.content, 'html.parser')
        convert = soup.find_all('span', {'class': 'DFlfde SwHCTb', 'data-precision': 2})
        return str(convert[0])

    def get_rates(self):
        found_rates = re.findall(r'\d{,2}[.,]\d{,5}', self.parse_html())
        self.rate = float(found_rates[0])
        self.round_rate = float(found_rates[1].replace(',', '.'))


class ExchangeBot:

    def __init__(self, rate_processing):
        self.rates_class = rate_processing

    def process_bot(self):
        bot = telebot.TeleBot(TG_TOKEN)

        @bot.message_handler(commands=['start'])
        def send_welcome(message):
            bot.send_message(message.chat.id, "Добро пожаловать, {}!\nЯ - ExchangeBot. Подскажу тебе актуальный курс доллара "
                                      "и евро на данный момент. Чуть позже у меня добавится возможность предупреждать "
                                      "тебя о достижении долларом "
                                      "или евро курса, который ты укажешь сам!".format(message.from_user.first_name))

            markup = types.ReplyKeyboardMarkup(row_width=2)
            itembtn1 = types.KeyboardButton('a')
            itembtn2 = types.KeyboardButton('v')
            itembtn3 = types.KeyboardButton('d')
            markup.add(itembtn1, itembtn2, itembtn3)
            bot.send_message(message.chat.id, "Choose one letter:", reply_markup=markup)

        @bot.message_handler(commands=['help'])
        def send_welcome(message):
            bot.reply_to(message, "Для получения актуального курса доллара напиши Привет")

        @bot.message_handler(content_types=['text'])
        def get_text_messages(message):
            if message.text == "Привет":
                bot.send_message(message.from_user.id,
                                 "Привет, курс доллара на сегодня = {}.".format(self.rates_class.rate))
            else:
                bot.send_message(message.chat.id, "Я тебя не понимаю. Напиши /help.")

        bot.polling()


def main():
    rate_processing = RateProcessing()
    rate_processing.get_rates()
    exchange_bot = ExchangeBot(rate_processing)
    exchange_bot.process_bot()


if __name__ == '__main__':
    main()
