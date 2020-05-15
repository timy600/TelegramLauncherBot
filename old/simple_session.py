import requests
import telepot
import json
s = requests.Session()

userName = {'userName': 'Thibz'}
location = {'location': 'Treuch'}
launchStatus = {'launchStatus': False}
launchChatId = {'launchChatId': False}
launchRight = {'launchRight': 10000}
launchLeft = {'launchLeft': 0}


set_cookie_url = 'https://httpbin.org/cookies/set'
get_cookies_url = "http://httpbin.org/cookies"

s.get(set_cookie_url, params=userName)
s.get(set_cookie_url, params=location)
s.get(set_cookie_url, params=launchStatus)
s.get(set_cookie_url, params=launchChatId)
s.get(set_cookie_url, params=launchRight)
s.get(set_cookie_url, params=launchLeft)

r = s.get(get_cookies_url)
print(r.text)
print(r.json())
print(type(r.json()))
if r.json()['cookies']['launchLeft'] == "False":
    print('YOLOLOLOLOLO')

bot = telepot.Bot("1210920754:AAHEO21N0TL7NnuLbI3ZJ_TmXgPKXkF9ViQ")
print(bot.getMe())
id = 1210920754 #id Thibs_bot
id = 1015798095 #id Thibaut

response = bot.getUpdates()
print(response)

from telepot.loop import MessageLoop
def handle(msg):
    chat_id = msg['chat']['id']
    command = msg['text']


    #print 'Got command: %s' % command
    if command == 'french':
        bot.sendMessage(chat_id, "Bien le bonjour")
    elif command == 'spanish':
        bot.sendMessage(chat_id, "Hola todos")
    elif command == 'photo':
        bot.sendPhoto(chat_id, URL)
    else:
        bot.sendMessage(chat_id, "I don't understand")

MessageLoop(bot, handle).run_as_thread()
