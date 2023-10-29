from dotenv import load_dotenv


load_dotenv()  # take environment variables from .env.

from os import getenv


TELEGRAM_TOKEN_2 = getenv("TELEGRAM_TOKEN")
