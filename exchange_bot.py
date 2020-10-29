import os
import time
import telebot
import sqlite3
from datetime import datetime
from rate_processing import RateProcessing as RPClass
from currency_level import CurrencyLevel as CLClass


class ExchangeBot:

    def __init__(self, clclass: CLClass):
        self.clclass = clclass
        self.tg_token = os.getenv('TG_TOKEN')
        self.menu = None
        self.markup = None
        self.bot = telebot.TeleBot(self.tg_token, num_threads=5)
        self.currency_variety_dict = {
            "Евро (€)": ["EUR", "€"],
            "Доллар ($)": ["USD", "$"],
            "Швейцарский франк (₣)": ["CHF", "₣"],
            "Биткойн (₿)": ["BTC", "₿"]
        }

    def welcome_user(self):
        # Приветственное сообщение в чате
        @self.bot.message_handler(commands=['start'])
        def send_welcome(message):
            self.bot.send_message(message.chat.id,
                                  "Добро пожаловать, {}!\nЯ - ExchangeBot. Подскажу Вам актуальный курс валют "
                                  "на данный момент. \nСписок доступных валют доступен по команде /currencies.\n"
                                  "Нужна помощь? Воспользуйтесь командой /help.\nДля вызова главного меню из любого "
                                  "места программы воспользуйтесь командой /menu.".format(message.from_user.first_name),
                                  reply_markup=self.markup)
            time.sleep(1)
            self.show_main_menu(message)

    def help_user(self):
        # Помогает пользователю подсказкой
        @self.bot.message_handler(commands=['help'])
        def send_help(message):
            self.bot.send_message(message.chat.id, "Чтобы не вводить каждый раз команды через слеш (/),"
                                                   " воспользуйтесь клавиатурой с командами. Это гораздо быстрее "
                                                   "и проще.")

    def currencies(self):
        # Выдает спиок поддерживаемых валют
        @self.bot.message_handler(commands=['currencies'])
        def send_currencies(message):
            string = 'Поддерживаются следующие валюты:'
            for item in self.currency_variety_dict.keys():
                string += f'\n{item}'
            self.bot.send_message(message.chat.id, string)

    def button_menu(self, params):
        # Шаблон всех меню
        self.menu = telebot.types.ReplyKeyboardMarkup()
        for item in params:
            self.menu.add(item)

    def show_main_menu(self, message):
        # Главное меню
        self.button_menu(('Узнать курс валюты', 'Установить уровень валюты', 'Отслеживаемые валюты'))
        self.bot.send_message(message.chat.id, "Выберите нужную опцию:", reply_markup=self.menu)
        self.show_button_menu()

    def show_button_menu(self):
        # Обработка в главном меню
        @self.bot.message_handler(content_types=['text'])
        def button_menu(message):
            if message.text == 'Узнать курс валюты':
                self.rate_menu(message)
                self.bot.register_next_step_handler(message, self.process_rate_exchange)
            elif message.text == 'Установить уровень валюты':
                self.rate_menu(message)
                self.bot.register_next_step_handler(message, self.process_currency_level)
            else:
                self.bot.send_message(message.chat.id, 'Я тебя не понимаю, повтори запрос.')
                self.show_button_menu()
            # elif message.text in list(self.currency_variety_dict.keys()):
            #     self.menu = None
            #     self.bot.edit_message_text(chat_id=call.message.chat.id,
            #                                message_id=call.message.message_id,
            #                                text=f"Выбрана валюта: {self.currency_variety_dict[call.data][0]}.\n"
            #                                     f"Идет обработка запроса.\nПару секунд, пожалуйста.",
            #                                reply_markup=self.menu)
            #     self.process_rate_exchange(call)
            # elif call.data in ['{} level'.format(self.currency_variety_dict[item][0])
            #                    for item in self.currency_variety_dict.keys()]:
            #     if len(self.temp_list) == 0:
            #         self.temp_list.append(call.data)
            #         self.menu = None
            #         self.bot.edit_message_text(chat_id=call.message.chat.id,
            #                                    message_id=call.message.message_id,
            #                                    text=f"Выбрана валюта: {call.data[0:3]}.\n"
            #                                         f"Установите ее уровень в ответном сообщении.",
            #                                    reply_markup=self.menu)
            #         self.bot.register_next_step_handler_by_chat_id(
            #             call.message.chat.id,
            #             self.process_currency_level,
            #             call.data[0:3]
            #         )
            #     else:
            #         self.menu = None
            #         self.bot.edit_message_text(chat_id=call.message.chat.id,
            #                                    message_id=call.message.message_id,
            #                                    text="Имеется активный запрос уровня валюты. "
            #                                         "Заполните его, пожалуйста.",
            #                                    reply_markup=self.menu)
            # elif call.data == 'Отслеживаемые валюты':
            #     if self.currency_levels_dict.get(call.from_user.id) is None or \
            #             not self.currency_levels_dict[call.from_user.id]:
            #         self.bot.send_message(call.message.chat.id, 'У Вас пока нет отслеживаемых валют.')
            #     else:
            #         self.bot.send_message(call.message.chat.id,
            #                               'Отсеживаются следующие валюты:\n{}'.format(
            #                                   '\n'.join(self.currency_levels_dict[call.from_user.id].keys()))
            #                               )

        # @self.bot.message_handler(content_types=['text'])
        # def main_menu(message):
        #     self.bot.send_message(message.chat.id, "Я Вас не понял. Выберите, пожалуйста, одну из опций из списка "
        #                                            "или воспользуйтесь клавиатурой с командами.")
        #
        #

    def rate_menu(self, message):
        self.button_menu(list(self.currency_variety_dict.keys()))
        self.bot.send_message(message.chat.id, "Выберите нужную валюту:", reply_markup=self.menu)

    def process_rate_exchange(self, message):
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
                                      datetime.utcfromtimestamp(curr_value[1]).strftime('%d.%m.%Y %H:%M:%S')
                                  )
                                  )
            self.show_main_menu(message)
        else:
            self.bot.send_message(message.chat.id, 'Вы ввели валюту неверно. Поробуйте выбрать из списка.')
            self.bot.register_next_step_handler(message, self.process_rate_exchange)

    def process_currency_level(self, message):
        try:
            self.clclass.set_level(message.from_user.id, key, float(message.text))
            self.bot.send_message(message.chat.id, "Установлен следующий уровень для {}: {}.\n"
                                                   "Ожидайте уведомления.".format(key, float(message.text)))

            # self.check_currency_level(message, message.from_user.id, key)
        except ValueError:
            self.bot.send_message(message.chat.id, "Это не число. Введите уровень валюты снова, пожалуйста.")
            self.bot.register_next_step_handler(message, self.process_currency_level)

    # with concurrent.futures.ThreadPoolExecutor() as executor:
    #     future = executor.submit(CurrencyLevel(curr_key, self.currency_levels_dict[user_id_key][curr_key]).execute)
    #     if not future.result():
    #         self.bot.send_message(message.chat.id, "{}, поздравляю! {} упал до выбранного "
    #                                                "Вами уровня. Можно менять :)".format(
    #             message.from_user.first_name, curr_key))
    #         self.currency_levels_dict[user_id_key].pop(curr_key)

    def execute(self):
        self.welcome_user()
        self.help_user()
        self.currencies()
        self.bot.infinity_polling(True)


rpclass = RPClass(30)
rpclass.execute()
clclass = CLClass(rpclass)
ExchangeBot(clclass).execute()
