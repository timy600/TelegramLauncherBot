import telepot
import telepot.loop
import requests


class TelegramBot():
    """
    Interface for telegram bot API. Each bot maintains many
    ChatSessions that are handled by classes
    """

    def __init__(self, token):
        """
        :param token: a bot authorization token, can be obtained from the @BotFather bot.
        """
        self._token = token
        self._bot = telepot.Bot(token)
        self._set_cookie_url = 'https://httpbin.org/cookies/set'
        self._get_cookies_url = 'https://httpbin.org/cookies'
        self._chat_id_to_session = {}

    @staticmethod
    def _parse_command(msg_text):
        """
        Parse message text as /<command> [argument]
        Further parsing of `argument` is left for specific
        implementations of `AbstractTelegramChatSession.handle_command`
        """
        if not msg_text.startswith('/'):
            raise ValueError('The command must start with /')

        command_and_arg = msg_text[1:].strip().split(' ', 1)
        command = command_and_arg[0]
        arg = command_and_arg[1] if len(command_and_arg) > 1 else ''
        return command, arg

    def _extract_photo_url(self, photo_sizes):
        # Telegram prepares several resized versions of the image,
        # we chose the biggest, assuming it's the original one
        photo_id = max(photo_sizes, key=lambda x: x['width'] * x['height'])['file_id']
        photo_path = self._bot.getFile(photo_id)['file_path']
        return 'https://api.telegram.org/file/bot{token}/{path}'.format(token=self._token, path=photo_path)

    def _init_chat_session(self, chat_id, **session_kwargs):
        session = requests.Session()
        launch_conversation = {'launchConversation': False}
        chat_id = {'chat_id': chat_id}
        session.get(self._set_cookie_url, params=launch_conversation)
        session.get(self._set_cookie_url, params=chat_id)
        return session

    def _get_chat_session(self, session):
        r = self.session.get(self._get_cookies_url)
        return r.text

    def run(self, **session_kwargs):
        def _handler(msg):
            content_type, chat_type, chat_id = telepot.glance(msg)

            if chat_id not in self._chat_id_to_session:
                self._chat_id_to_session[chat_id] = self._init_chat_session(chat_id, **session_kwargs)
                print("initialize chat session")
                print(self._chat_id_to_session[chat_id])

            #session = self._chat_id_to_session[chat_id]

            if content_type == 'text' and msg['text'].startswith('/'):
                command, arg = self._parse_command(msg['text'])
                if command == 'start':
                    session = self._chat_id_to_session[chat_id] = self._init_chat_session(
                        chat_id, **session_kwargs)

                return session.handle_command(command, arg)

            if content_type == 'text':
                cookies = self._chat_id_to_session[chat_id].get(self._get_cookies_url).json()
                print(cookies)
                #return session.handle_text_message(msg['text'], msg)
                positive_response
                if msg['text'] == "yes":
                    bisect("left")
                elif msg['text'] == "no":
                    bisect("right")
                else:
                    self.
                return "my_test"

            if content_type == 'photo':
                photo_url = self._extract_photo_url(msg['photo'])
                return session.handle_photo_message(photo_url, msg)

            return session.default_handle_message(msg)

        telepot.loop.MessageLoop(self._bot, _handler).run_forever()


NewToken = "1210920754:AAHEO21N0TL7NnuLbI3ZJ_TmXgPKXkF9ViQ"
#bot = telepot.Bot(NewToken)
#bot.deleteWebhook()
NewBot = TelegramBot(NewToken)
NewBot.run()

#print(NewBot._get_chat_session())
