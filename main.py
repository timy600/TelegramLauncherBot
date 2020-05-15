from abstractChatSession import TelegramBot, LaunchFrameXChatSession

with open("telegram_token.txt", "r") as file:
    token = file.read()

TelegramBot(token).run(LaunchFrameXChatSession)
