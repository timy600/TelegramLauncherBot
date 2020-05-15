import telepot

import sys
import time
import random
import datetime

import requests
s = requests.session()

s.get('http://httpbin.org/cookies/set/sessioncookie/123456789')
r = s.get("http://httpbin.org/cookies")

print r.text
# '{"cookies": {"sessioncookie": "123456789"}}'
from framex_utility import
bot = telepot.Bot("1210920754:AAHEO21N0TL7NnuLbI3ZJ_TmXgPKXkF9ViQ")
bot.getMe()
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






def run(self, session_class, **session_kwargs):
        """
        :param session_class: subclass of AbstractTelegramChat
        """
        self._logger.info('Started a new chat bot {}'.format(self._bot.getMe()))

        def _handler(msg):
            content_type, chat_type, chat_id = telepot.glance(msg)

            if chat_id not in self._chat_id_to_session:
                self._chat_id_to_session[chat_id] = self._init_chat_session(chat_id, session_class, **session_kwargs)

            session = self._chat_id_to_session[chat_id]

            if content_type == 'text' and msg['text'].startswith('/'):
                command, arg = self._parse_command(msg['text'])
                if command == 'start':
                    session = self._chat_id_to_session[chat_id] = self._init_chat_session(
                        chat_id, session_class, **session_kwargs)

                return session.handle_command(command, arg)

            if content_type == 'text':
                return session.handle_text_message(msg['text'], msg)

            if content_type == 'photo':
                photo_url = self._extract_photo_url(msg['photo'])
                return session.handle_photo_message(photo_url, msg)

            return session.default_handle_message(msg)

        telepot.loop.MessageLoop(self._bot, _handler).run_forever()
