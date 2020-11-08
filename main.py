import telebot
from rate_processing import RateProcessing as RPClass
from exchange_bot import ExchangeBot as EBClass
from flask import Flask, request
import time

rpclass = RPClass(300)
ebclass = EBClass(rpclass)
ebclass.bot.remove_webhook()
time.sleep(1)
ebclass.bot.set_webhook(url='https://andrey19972004.pythonanywhere.com/{}'.format(ebclass.flsk_url))
ebclass.bot.enable_save_next_step_handlers(delay=2)
ebclass.bot.load_next_step_handlers()
rpclass.execute()
ebclass.execute()

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello, World!'


@app.route('/{}'.format(ebclass.flsk_url), methods=["POST"])
def webhook():
    ebclass.bot.process_new_updates([telebot.types.Update.de_json(request.stream.read().decode("utf-8"))])
    return "!", 200
