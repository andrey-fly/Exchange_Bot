import os
import threading
import telebot
import sqlite3
from datetime import datetime
from rate_processing import RateProcessing as RPClass


class ExchangeBot:
    """
    Класс, который описывает логику бота
    """

    def __init__(self, rplass: RPClass):
        """
        Инициализация бота
        :param rplass: RateProcessing Class Object
        """
        self.rpclass = rplass
        self.tg_token = os.environ.get('TG_TOKEN')
        self.sec_url = os.environ.get('SEC_URL')
        self.menu = None
        self.markup = None
        self.bot = telebot.TeleBot(self.tg_token)
        self.currency_variety_dict = {
            "Евро": ["EUR", "€"],
            "Доллар": ["USD", "$"],
            "Швейцарский франк": ["CHF", "₣"],
            "Биткойн": ["BTC", "₿"]
        }

    def welcome_user(self):
        """
        Приветственное сообщение в чате
        :return: None
        """

        @self.bot.message_handler(commands=['start'])
        def send_welcome(message):
            self.bot.send_message(message.chat.id,
                                  "Добро пожаловать, {}!\nЯ - ExchangeBot. Подскажу тебе актуальный курс валют "
                                  "на данный момент. \nСписок доступных валют доступен по команде /currencies.\n"
                                  "Нужна помощь? Воспользуйтесь командой /help.".format(message.from_user.first_name),
                                  reply_markup=self.markup)
            self.show_main_menu(message)

    def help_user(self):
        """
        Команда помощи пользователю
        :return: None
        """

        @self.bot.message_handler(commands=['help'])
        def send_help(message):
            self.bot.send_message(message.chat.id, "Чтобы не вводить каждый раз команды через слеш (/),"
                                                   " воспользуйтесь клавиатурой с командами. Это гораздо быстрее "
                                                   "и проще.")

    def currencies(self):
        """
        Команда выдачи списка поддерживаемых валют
        :return:None
        """

        @self.bot.message_handler(commands=['currencies'])
        def send_currencies(message):
            string = 'Поддерживаются следующие валюты:'
            for item in self.currency_variety_dict.keys():
                string += f'\n{item}'
            self.bot.send_message(message.chat.id, string)

    def button_menu(self, params: tuple):
        """
        Шаблон всех меню
        :param params: tuple
        :return: None
        """
        self.menu = telebot.types.ReplyKeyboardMarkup()
        for item in params:
            self.menu.add(item)

    def show_main_menu(self, message: telebot.types.Message):
        """
        Показ главного меню
        :param message: telebot.types.Message
        :return: None
        """
        self.button_menu(('Узнать курс валюты', 'Установить уровень валюты', 'Отслеживаемые валюты'))
        self.bot.send_message(message.chat.id, "Выберите нужную опцию:", reply_markup=self.menu)

    def process_main_menu(self):
        """
        Обработка главного меню
        :return: None
        """

        @self.bot.message_handler(content_types=['text'])
        def button_menu(message):
            if message.text == 'Узнать курс валюты':
                self.rate_menu(message)
                self.bot.register_next_step_handler(message, self.process_rate_exchange)
            elif message.text == 'Установить уровень валюты':
                self.rate_menu(message)
                self.bot.register_next_step_handler(message, self.process_currency_level)
            elif message.text == 'Отслеживаемые валюты':
                flw_cur = self.rpclass.get_flw_cur(message.from_user.id)
                fin_str = 'Список отслеживаемых тобой валют и их уровней:'
                if flw_cur:
                    for item in flw_cur:
                        fin_str = fin_str + '\n{} - {} ₽'.format(item[3], item[4])
                    self.bot.send_message(message.chat.id, fin_str)
                else:
                    self.bot.send_message(message.chat.id, 'У тебя нет отслеживаемых валют.')
            else:
                self.bot.send_message(message.chat.id, 'Я тебя не понимаю, повтори запрос.')
                self.process_main_menu()

    def rate_menu(self, message):
        # Меню выбора валюты
        self.button_menu(tuple(self.currency_variety_dict.keys()) + ('Назад',))
        self.bot.send_message(message.chat.id, "Выберите нужную валюту:", reply_markup=self.menu)

    def process_rate_exchange(self, message):
        # Получение курса валют из БД
        if message.text != 'Назад':
            if message.text in list(self.currency_variety_dict.keys()):
                conn = sqlite3.connect("currencies_db.db")
                cursor = conn.cursor()
                key = self.currency_variety_dict[message.text][0]
                curr_value = cursor.execute('SELECT curr_value, time FROM updated_currencies '
                                            'WHERE curr_code = ?', (key,)).fetchone()
                self.bot.send_message(message.chat.id,
                                      "1 {} = {:.2f} ₽\n"
                                      "{} (UTC+0)".format(
                                          self.currency_variety_dict[message.text][1],
                                          curr_value[0],
                                          datetime.utcfromtimestamp(curr_value[1]).strftime('%d.%m.%Y %H:%M')
                                      )
                                      )
                self.show_main_menu(message)
            else:
                self.bot.send_message(message.chat.id, 'Вы ввели название валюты неверно. Поробуйте выбрать из списка.')
                self.bot.register_next_step_handler(message, self.process_rate_exchange)
        else:
            self.bot.register_next_step_handler(message, self.process_main_menu)

    def process_currency_level(self, message):
        # Процесс установки уровня валюты
        if message.text in list(self.currency_variety_dict.keys()):
            self.bot.send_message(message.chat.id, 'Выбрана валюта: {}\n'
                                                   'Установите ее уровень в ответном сообщении.'.format(message.text))
            self.bot.register_next_step_handler(message,
                                                self.set_currency_level,
                                                self.currency_variety_dict[message.text][0])
        else:
            self.bot.send_message(message.chat.id, 'Вы ввели название валюты неверно. Поробуйте выбрать из списка.')
            self.bot.register_next_step_handler(message, self.process_currency_level)

    def set_currency_level(self, message, key):
        # Непосредстенно сама установка уровня валюты в БД
        try:
            flt_value = float(message.text.replace(',', '.'))
            self.rpclass.set_level(message.from_user.id,
                                   message.from_user.first_name,
                                   message.chat.id,
                                   key,
                                   flt_value)
            self.bot.send_message(message.chat.id, "Установлен следующий уровень для {}: {}.\n"
                                                   "Ожидайте уведомления.".format(key, flt_value))
            self.show_main_menu(message)
        except ValueError:
            self.bot.send_message(message.chat.id, "Это не число. Введите уровень валюты снова, пожалуйста.")
            self.bot.register_next_step_handler(message, self.set_currency_level, key)

    def curr_thread(self):
        while True:
            if self.rpclass.users_to_send and self.rpclass.flag_upd_uts:
                for key in self.rpclass.users_to_send.keys():
                    for item in self.rpclass.users_to_send[key]:
                        self.bot.send_message(item[2], '{}, поздравляю! Уровень валюты {} опустился до {}. '
                                                       'Можно менять :)'.format(item[1],
                                                                                item[3],
                                                                                item[4]))
                self.rpclass.users_to_send = {}
                self.rpclass.flag_upd_uts = False

    def execute(self):
        self.bot.remove_webhook()
        self.bot.set_webhook(url='https://protected-oasis-53938.herokuapp.com/' + self.sec_url)
        self.welcome_user()
        self.help_user()
        self.currencies()
        self.process_main_menu()
        threading.Thread(target=self.curr_thread).start()
