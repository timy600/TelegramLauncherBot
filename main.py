from abstractChatSession import TelegramBot, ReversedChatSession

with open("telegram_token.txt", "r") as file:
    token = file.read()

TelegramBot(token).run(ReversedChatSession)
