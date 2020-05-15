import telepot
bot = telepot.Bot("1210920754:AAHEO21N0TL7NnuLbI3ZJ_TmXgPKXkF9ViQ")
bot.getMe()
id = 1210920754 #id Thibs_bot
id = 1015798095 #id Thibaut
id_chat = -424370076 # Chat with Diamora
chat_id = -424370076
#from pprint import pprint
response = bot.getUpdates()
print(response)
#pprint(response)

bot.sendMessage(id, 'Hey!')
bot.sendMessage(id_chat, 'Hola soy el Bot de Thibaut, y me gustan las cerezas')

import sys
import time
import random
import datetime

URL = "https://www.pauloeuvreart.com/couch/uploads/image/reproductions_theme/rey_felipe_vi.jpeg"
# SEND MESSAGE
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

bot = telepot.Bot(id)
bot.message_loop(handle)
print 'I am listening ...'

while 1:
    time.sleep(10)



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
