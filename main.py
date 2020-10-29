import os
import time
import telebot
from rate_processing import RateProcessing as RPClass
from currency_level import CurrencyLevel as CLClass


# class ExchangeBot:
#
#     def __init__(self, rpclass: RPClass, clclass: CLClass):
#         self.rpclass = rpclass
#         self.clclass = clclass
#         self.tg_token = os.getenv('TG_TOKEN')
#         self.menu = None
#         self.markup = None
#         self.bot = telebot.TeleBot(self.tg_token, num_threads=5)
#         self.currency_variety_dict = {
#             "Евро (€)": ["EUR", "€"],
#             "Доллар ($)": ["USD", "$"],
#             "Швейцарский франк (₣)": ["CHF", "₣"],
#             "Биткойн (₿)": ["BTC", "₿"]
#         }
#         self.currency_levels_dict = {}
#         self.temp_list = []
#
#     def keyboard_command(self):
#         # Шаблон клавиатуры
#         commands = [('/start', '/menu'), ('/help', '/currencies')]
#         self.markup = telebot.types.ReplyKeyboardMarkup(row_width=2)
#         for item in commands:
#             self.markup.add(telebot.types.KeyboardButton(text=item[0]),
#                             telebot.types.KeyboardButton(text=item[1])
#                             )
#
#     def welcome_user(self):
#         # Приветственное сообщение в чате
#         @self.bot.message_handler(commands=['start'])
#         def send_welcome(message):
#             self.keyboard_command()
#             self.bot.send_message(message.chat.id,
#                                   "Добро пожаловать, {}!\nЯ - ExchangeBot. Подскажу Вам актуальный курс валют "
#                                   "на данный момент. \nСписок доступных валют доступен по команде /currencies.\n"
#                                   "Нужна помощь? Воспользуйтесь командой /help.\nДля вызова главного меню из любого "
#                                   "места программы воспользуйтесь командой /menu.".format(message.from_user.first_name),
#                                   reply_markup=self.markup)
#             time.sleep(1)
#             self.currency_levels_dict[message.from_user.id] = {}
#             self.show_main_menu(message)
#
#     def help_user(self):
#         # Помогает пользователю подсказкой
#         @self.bot.message_handler(commands=['help'])
#         def send_help(message):
#             self.bot.send_message(message.chat.id, "Чтобы не вводить каждый раз команды через слеш (/),"
#                                                    " воспользуйтесь клавиатурой с командами. Это гораздо быстрее "
#                                                    "и проще.")
#
#     def currencies(self):
#         # Выдает спиок поддерживаемых валют
#         @self.bot.message_handler(commands=['currencies'])
#         def send_currencies(message):
#             string = 'Поддерживаются следующие валюты:'
#             for item in self.currency_variety_dict.keys():
#                 string += f'\n{item}'
#             self.bot.send_message(message.chat.id, string)
#
#     def command_main_menu(self):
#         # Помогает пользователю подсказкой
#         @self.bot.message_handler(commands=['menu'])
#         def send_menu(message):
#             self.show_main_menu(message)
#
#     def button_menu(self, params):
#         # Шаблон всех меню
#         self.menu = telebot.types.InlineKeyboardMarkup()
#         for item in params:
#             self.menu.add(telebot.types.InlineKeyboardButton(text=item, callback_data=item))
#
#     def show_main_menu(self, message):
#         # Главное меню
#         self.button_menu(('Узнать курс валюты', 'Установить уровень валюты', 'Отслеживаемые валюты'))
#         self.bot.send_message(message.chat.id, "Выберите нужную опцию:", reply_markup=self.menu)
#         self.main_callback_handler()
#
#     def main_callback_handler(self):
#         # Обработка в главном меню
#         @self.bot.callback_query_handler(func=lambda call: True)
#         def button_menu(call):
#             if call.data == 'Узнать курс валюты':
#                 self.get_currency_rate_menu(call)
#             elif call.data == 'Установить уровень валюты':
#                 self.set_currency_level_menu(call)
#             elif call.data in list(self.currency_variety_dict.keys()):
#                 self.menu = None
#                 self.bot.edit_message_text(chat_id=call.message.chat.id,
#                                            message_id=call.message.message_id,
#                                            text=f"Выбрана валюта: {self.currency_variety_dict[call.data][0]}.\n"
#                                                 f"Идет обработка запроса.\nПару секунд, пожалуйста.",
#                                            reply_markup=self.menu)
#                 self.process_rate_exchange(call)
#             elif call.data in ['{} level'.format(self.currency_variety_dict[item][0])
#                                for item in self.currency_variety_dict.keys()]:
#                 if len(self.temp_list) == 0:
#                     self.temp_list.append(call.data)
#                     self.menu = None
#                     self.bot.edit_message_text(chat_id=call.message.chat.id,
#                                                message_id=call.message.message_id,
#                                                text=f"Выбрана валюта: {call.data[0:3]}.\n"
#                                                     f"Установите ее уровень в ответном сообщении.",
#                                                reply_markup=self.menu)
#                     self.bot.register_next_step_handler_by_chat_id(
#                         call.message.chat.id,
#                         self.process_currency_level,
#                         call.data[0:3]
#                     )
#                 else:
#                     self.menu = None
#                     self.bot.edit_message_text(chat_id=call.message.chat.id,
#                                                message_id=call.message.message_id,
#                                                text="Имеется активный запрос уровня валюты. "
#                                                     "Заполните его, пожалуйста.",
#                                                reply_markup=self.menu)
#             elif call.data == 'Отслеживаемые валюты':
#                 if self.currency_levels_dict.get(call.from_user.id) is None or \
#                         not self.currency_levels_dict[call.from_user.id]:
#                     self.bot.send_message(call.message.chat.id, 'У Вас пока нет отслеживаемых валют.')
#                 else:
#                     self.bot.send_message(call.message.chat.id,
#                                           'Отсеживаются следующие валюты:\n{}'.format(
#                                               '\n'.join(self.currency_levels_dict[call.from_user.id].keys()))
#                                           )
#
#         @self.bot.message_handler(content_types=['text'])
#         def main_menu(message):
#             self.bot.send_message(message.chat.id, "Я Вас не понял. Выберите, пожалуйста, одну из опций из списка "
#                                                    "или воспользуйтесь клавиатурой с командами.")
#
#     def get_currency_rate_menu(self, call):
#         self.button_menu(list(self.currency_variety_dict.keys()))
#         self.bot.send_message(call.message.chat.id, "Выберите нужную валюту:", reply_markup=self.menu)
#
#     def set_currency_level_menu(self, call):
#         self.menu = telebot.types.InlineKeyboardMarkup()
#         for item in list(self.currency_variety_dict.keys()):
#             self.menu.add(telebot.types.InlineKeyboardButton(
#                 text=item,
#                 callback_data='{} level'.format(self.currency_variety_dict[item][0]))
#             )
#         self.bot.send_message(call.message.chat.id, "Выберите нужную валюту:", reply_markup=self.menu)
#
#     def process_rate_exchange(self, call):
#         self.rates_class.currencies_ref_dict_key = self.currency_variety_dict[call.data][0]
#         self.bot.send_message(call.message.chat.id,
#                               "1 {} = {:.2f} ₽".format(
#                                   self.currency_variety_dict[call.data][1],
#                                   self.rates_class.get_rate())
#                               )
#
#     def process_currency_level(self, message, key):
#         try:
#             self.currency_levels_dict[message.from_user.id][key] = float(message.text)
#             self.bot.send_message(message.chat.id, "Установлен следующий уровень для {}: {}.\n"
#                                                    "Ожидайте уведомления.".format(key,
#                                                                                   self.currency_levels_dict[
#                                                                                       message.from_user.id][key]))
#             self.temp_list.clear()
#             # self.check_currency_level(message, message.from_user.id, key)
#         except ValueError:
#             self.bot.send_message(message.chat.id, "Это не число. Введите уровень валюты снова, пожалуйста.")
#             self.bot.register_next_step_handler_by_chat_id(message.chat.id, self.process_currency_level, key)
#
#     def check_currency_level(self):
#         pass
#
#         # with concurrent.futures.ThreadPoolExecutor() as executor:
#         #     future = executor.submit(CurrencyLevel(curr_key, self.currency_levels_dict[user_id_key][curr_key]).execute)
#         #     if not future.result():
#         #         self.bot.send_message(message.chat.id, "{}, поздравляю! {} упал до выбранного "
#         #                                                "Вами уровня. Можно менять :)".format(
#         #             message.from_user.first_name, curr_key))
#         #         self.currency_levels_dict[user_id_key].pop(curr_key)
#
#     def execute(self):
#         self.welcome_user()
#         self.help_user()
#         self.currencies()
#         self.command_main_menu()
#         self.bot.infinity_polling(True)


def main():
    exchange_bot = ExchangeBot(RPClass())
    exchange_bot.execute()
    # RPClass().run(60)


if __name__ == '__main__':
    main()
