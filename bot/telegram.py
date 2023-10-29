from telebot.async_telebot import AsyncTeleBot
import asyncio


# Создаем класс Telegram для обработки сообщений в Telegram
class Telegram:
    def __init__(self, token: str, handler):
        self.token = token
        bot = self.bot = AsyncTeleBot(token)  # Инициализируем бота с указанным токеном
        self.handler = handler

        # Определяем обработчик для текстовых сообщений, местоположений, фотографий и документов
        @self.bot.message_handler(
            func=lambda message: True,
            content_types=["location", "text", "photo", "document"],
        )
        async def handle_message(message):
            await handler(message, bot)  # Передаем сообщение обработчику

        # Определяем обработчик для inline-кнопок (коллбэков)
        @self.bot.callback_query_handler(func=lambda call: True)
        async def call_beck_admin1(call):
            await handler(call, bot)  # Передаем коллбэк обработчику

        asyncio.run(
            bot.polling()
        )  # Запускаем асинхронный процесс получения сообщений из Telegram


# Пример использования:
# Создаем экземпляр класса Telegram и передаем в него токен и обработчик
# (handler) для обработки входящих сообщений и обратных вызовов.
# Токен бота должен быть получен в BotFather на платформе Telegram.
# telegram = Telegram("YOUR_BOT_TOKEN", your_message_handler_function)
