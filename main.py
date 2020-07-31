import concurrent.futures
import datetime
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
                   '%80%D0%B0&oq=rehc&aqs=chrome.1.69i57j0l7.2693j0j8&sourceid=chrome&ie=UTF-8',
            'CHF': 'https://www.google.com/search?q=%D1%88%D0%B2%D0%B5%D0%B9%D1%86%D0%B0%D1%80%D1%81%D0%BA%D0%B8%D0%'
                   'B9+%D1%84%D1%80%D0%B0%D0%BD%D0%BA&oq=idtqwfhcrb&aqs=chrome.1.69i57j0l3j46l2j0l2.5304j1j8&sourcei'
                   'd=chrome&ie=UTF-8'
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
        if self.rate_processing.rate < self.my_level:
            return True
        else:
            return False

    def execute(self):
        while self.flag_on:
            time.sleep(10)
            if self.result_comparison():
                self.unexecute()
                return False

    def unexecute(self):
        self.flag_on = False


class ExchangeBot:

    def __init__(self, rate_processing: RateProcessing):
        self.rates_class = rate_processing
        self.tg_token = '1152544884:AAH-x7Gzd4RcX7sgOPLHKm1wV7OFxJ1YgPY'
        self.menu = None
        self.markup = None
        self.bot = telebot.TeleBot(self.tg_token, num_threads=1000)
        self.currency_variety_dict = {
            "Евро (€)": ["EUR", "€"],
            "Доллар ($)": ["USD", "$"],
            "Швейцарский франк (₣)": ["CHF", "₣"]
        }
        self.currency_levels_dict = {}
        self.temp_list = []

    def keyboard_command(self):
        # Шаблон клавиатуры
        commands = [('/start', '/menu'), ('/help', '/currencies')]
        self.markup = telebot.types.ReplyKeyboardMarkup(row_width=2)
        for item in commands:
            self.markup.add(telebot.types.KeyboardButton(text=item[0]),
                            telebot.types.KeyboardButton(text=item[1])
                            )

    def welcome_user(self):
        # Приветственное сообщение в чате
        @self.bot.message_handler(commands=['start'])
        def send_welcome(message):
            self.keyboard_command()
            self.bot.send_message(message.chat.id,
                                  "Добро пожаловать, {}!\nЯ - ExchangeBot. Подскажу тебе актуальный курс валют "
                                  "на данный момент. \nСписок доступных валют доступен по команде /currencies.\n"
                                  "Нужна помощь? Воспользуйтесь командой /help.\nДля вызова главного меню из любого "
                                  "места программы воспользуйтесь командой /menu.".format(message.from_user.first_name),
                                  reply_markup=self.markup)
            time.sleep(1)
            self.currency_levels_dict[message.from_user.id] = {}
            self.show_main_menu(message)

    def help_user(self):
        # Помогает пользователю подсказкой
        @self.bot.message_handler(commands=['help'])
        def send_help(message):
            self.bot.send_message(message.chat.id, "Чтобы не вводить каждый раз команды через слеш (/),"
                                                   " воспользуйтесь клавиатурой с командами. Это гораздо быстрее "
                                                   "и проще.")

    def currencies(self):
        # Помогает пользователю подсказкой
        @self.bot.message_handler(commands=['currencies'])
        def send_currencies(message):
            string = 'Поддерживаются следующие валюты:'
            for item in self.currency_variety_dict.keys():
                string += f'\n{item}'
            self.bot.send_message(message.chat.id, string)

    def command_main_menu(self):
        # Помогает пользователю подсказкой
        @self.bot.message_handler(commands=['menu'])
        def send_menu(message):
            self.show_main_menu(message)

    def button_menu(self, params):
        # Шаблон всех меню
        self.menu = telebot.types.InlineKeyboardMarkup()
        for item in params:
            self.menu.add(telebot.types.InlineKeyboardButton(text=item, callback_data=item))

    def show_main_menu(self, message):
        self.button_menu(('Узнать курс валюты', 'Установить уровень валюты', 'Отслеживаемые валюты'))
        self.bot.send_message(message.chat.id, "Выберите нужную опцию:", reply_markup=self.menu)
        self.main_callback_handler()

    def main_callback_handler(self):
        @self.bot.callback_query_handler(func=lambda call: True)
        def button_menu(call):
            if call.data == 'Узнать курс валюты':
                self.get_currency_rate_menu(call)
            elif call.data == 'Установить уровень валюты':
                self.set_currency_level_menu(call)
            elif call.data in list(self.currency_variety_dict.keys()):
                self.menu = None
                self.bot.edit_message_text(chat_id=call.message.chat.id,
                                           message_id=call.message.message_id,
                                           text=f"Выбрана валюта: {self.currency_variety_dict[call.data][0]}.\n"
                                                f"Идет обработка запроса.\nПару секунд, пожалуйста.",
                                           reply_markup=self.menu)
                self.process_rate_exchange(call)
            elif call.data in ['{} level'.format(self.currency_variety_dict[item][0])
                               for item in self.currency_variety_dict.keys()]:
                if len(self.temp_list) == 0:
                    self.temp_list.append(call.data)
                    self.menu = None
                    self.bot.edit_message_text(chat_id=call.message.chat.id,
                                               message_id=call.message.message_id,
                                               text=f"Выбрана валюта: {call.data[0:3]}.\n"
                                                    f"Установите ее уровень в ответном сообщении.",
                                               reply_markup=self.menu)
                    self.bot.register_next_step_handler_by_chat_id(
                        call.message.chat.id,
                        self.process_currency_level,
                        call.data[0:3]
                    )
                else:
                    self.menu = None
                    self.bot.edit_message_text(chat_id=call.message.chat.id,
                                               message_id=call.message.message_id,
                                               text="Имеется активный запрос уровня валюты. "
                                                    "Заполните его, пожалуйста.",
                                               reply_markup=self.menu)
            elif call.data == 'Отслеживаемые валюты':
                if self.currency_levels_dict.get(call.from_user.id) is None or not self.currency_levels_dict[
                    call.from_user.id]:
                    self.bot.send_message(call.message.chat.id, 'У Вас пока нет отслеживаемых валют.')
                else:
                    self.bot.send_message(call.message.chat.id,
                                          'Отсеживаются следующие валюты:\n{}'.format(
                                              '\n'.join(self.currency_levels_dict[call.from_user.id].keys()))
                                          )

        @self.bot.message_handler(content_types=['text'])
        def main_menu(message):
            self.bot.send_message(message.chat.id, "Я Вас не понял. Выберите, пожалуйста, одну из опций из списка "
                                                   "или воспользуйтесь клавиатурой с командами.")

    def get_currency_rate_menu(self, call):
        self.button_menu(list(self.currency_variety_dict.keys()))
        self.bot.send_message(call.message.chat.id, "Выберите нужную валюту:", reply_markup=self.menu)

    def set_currency_level_menu(self, call):
        self.menu = telebot.types.InlineKeyboardMarkup()
        for item in list(self.currency_variety_dict.keys()):
            self.menu.add(telebot.types.InlineKeyboardButton(
                text=item,
                callback_data='{} level'.format(self.currency_variety_dict[item][0]))
            )
        self.bot.send_message(call.message.chat.id, "Выберите нужную валюту:", reply_markup=self.menu)

    def process_rate_exchange(self, call):
        self.rates_class.currencies_ref_dict_key = self.currency_variety_dict[call.data][0]
        self.rates_class.get_rates()
        self.bot.send_message(call.message.chat.id,
                              "На {}\n1 {} = {:.2f} ₽".format(
                                  datetime.datetime.fromtimestamp(call.message.date).strftime('%d.%m.%Y %H:%M'),
                                  self.currency_variety_dict[call.data][1],
                                  self.rates_class.round_rate)
                              )

    def process_currency_level(self, message, key):
        try:
            self.currency_levels_dict[message.from_user.id][key] = float(message.text)
            self.bot.send_message(message.chat.id, "Установлен следующий уровень для {}: {}.\n"
                                                   "Ожидайте уведомления.".format(key,
                                                                                  self.currency_levels_dict[
                                                                                      message.from_user.id][key]))
            self.temp_list.clear()
            self.check_currency_level(message, message.from_user.id, key)
        except ValueError:
            self.bot.send_message(message.chat.id, "Это не число. Введите уровень валюты снова, пожалуйста.")
            self.bot.register_next_step_handler_by_chat_id(message.chat.id, self.process_currency_level, key)

    def check_currency_level(self, message, user_id_key, curr_key):
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(CurrencyLevel(curr_key, self.currency_levels_dict[user_id_key][curr_key]).execute)
            if not future.result():
                self.bot.send_message(message.chat.id, "{}, поздравляю! {} упал до выбранного "
                                                       "Вами уровня. Можно менять :)".format(
                    message.from_user.first_name, curr_key))
                self.currency_levels_dict[user_id_key].pop(curr_key)

    def execute(self):
        self.welcome_user()
        self.help_user()
        self.currencies()
        self.command_main_menu()
        self.bot.infinity_polling(True)


def main():
    exchange_bot = ExchangeBot(RateProcessing())
    exchange_bot.execute()


if __name__ == '__main__':
    main()
