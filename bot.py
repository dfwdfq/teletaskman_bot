import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from dotenv import load_dotenv

class Bot:
    def __init__(self):
        load_dotenv()
        self.key = os.getenv("BOT_KEY")
        if not self.key:
            raise Exception("No 'BOT_KEY' in env variables!")
        self.app = Application.builder().token(self.key).build()

    def run(self):
        self.app.run_polling(poll_interval=5)
        
