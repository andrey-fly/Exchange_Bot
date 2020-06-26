import telebot

TG_TOKEN = '1152544884:AAEtSB-YpxGFgsWXcrTCIxrFe1PiJXYVpMo'


def main():
    bot = telebot.TeleBot(TG_TOKEN)

    @bot.message_handler(commands=['start', 'help'])
    def send_welcome(message):
        bot.reply_to(message, "Здесь будет описание бота")

    @bot.message_handler(content_types=['text'])
    def get_text_messages(message):
        if message.text == "Привет":
            bot.send_message(message.from_user.id, "Привет, сейчас я расскажу тебе курс на сегодня.")
        else:
            bot.send_message(message.from_user.id, "Я тебя не понимаю. Напиши /help.")

    # @bot.message_handler(func=lambda message: True)
    # def echo_all(message):
    #     bot.reply_to(message, message.text)

    bot.polling()


if __name__ == '__main__':
    main()
