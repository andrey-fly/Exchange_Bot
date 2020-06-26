import telebot
import requests
from bs4 import BeautifulSoup

TG_TOKEN = '1152544884:AAEtSB-YpxGFgsWXcrTCIxrFe1PiJXYVpMo'
DOLLAR_RUBLE = 'https://www.google.com/search?q=%D0%BA%D1%83%D1%80%D1%81+%D0%B4%D0%BE%D0%BB%D0%BB%D0%B0%' \
               'D1%80%D0%B0&oq=rehc&aqs=chrome.1.69i57j0l7.2693j0j8&sourceid=chrome&ie=UTF-8'
headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_4) AppleWebKit/537.36 (KHTML, like Gecko) '
                         'Chrome/83.0.4103.106 Safari/537.36'}


def get_rate_process():
    full_page = requests.get(DOLLAR_RUBLE, headers=headers)
    soup = BeautifulSoup(full_page.content, 'html.parser')
    convert = soup.find_all('span', {'class': 'DFlfde SwHCTb', 'data-precision': 2})
    found_tag = str(convert[0])
    index_str_rate = found_tag.find('data-value="')
    return found_tag[index_str_rate + 12:index_str_rate + 19]


def process_bot():
    bot = telebot.TeleBot(TG_TOKEN)

    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(message):
        bot.reply_to(message, "Здесь будет описание бота")

    @bot.message_handler(content_types=['text'])
    def get_text_messages(message):
        if message.text == "Привет":
            bot.send_message(message.from_user.id, "Привет, курс доллара на сегодня = {}.".format(get_rate_process()))
        else:
            bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши /help.")

    bot.polling()


def main():
    get_rate_process()
    process_bot()


if __name__ == '__main__':
    main()
