import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    def __init__(self):
        self.BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
        self.ADMIN_IDS = [os.getenv("ADMIN_IDS")]

config = Config()