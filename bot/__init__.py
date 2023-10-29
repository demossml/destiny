
from telegram import Telegram
from config import TELEGRAM_TOKEN_2
from bd.model import get_session, create_massage, Session
from state_machine import handle_message


async def handler(params, bot):
    message = create_massage(params)
    # print(message)
    session = get_session(message.user_id)
    session.message = message
    await handle_message(bot, message, session)


if __name__ == "__main__":
    bot = Telegram(TELEGRAM_TOKEN_2, handler)


