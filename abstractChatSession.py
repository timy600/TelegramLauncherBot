from abc import ABCMeta, abstractmethod

import telepot
import telepot.loop

import requests
from framex_utility import get_photo_url, FrameXBisector, VIDEO_NAME

class AbstractTelegramChatSession(metaclass=ABCMeta):
    """
    Specific implementations of a chat session should overload default
    message handler `default_handle_message`, and possibly some of specific
    handler like `handle_photo_message` or `handle_text_message`.
    `_register_command` can be used to register a specific command to be
    recognized by the bot along with a corresponding handler.
    """

    def __init__(self, bot, chat_id):
        super(AbstractTelegramChatSession, self).__init__()
        self._bot = bot
        self._chat_id = chat_id

        self._command_to_handler = {}
        # Default no-op /start command handler
        self._register_command(command='start', handler=lambda *args: None, description='Start or restart a session')
        self._register_command(
            command='help', handler=self._send_bot_help, description='Show bot info and a list of available commands')

    def _send_text(self, text, *args, **kwargs):
        self._bot.sendMessage(self._chat_id, text, *args, **kwargs)

    def _send_photo(self, photo, *args, **kwargs):
        self._bot.sendPhoto(self._chat_id, photo, *args, **kwargs)

    def handle_text_message(self, text, msg):
        return self.default_handle_message(msg)

    def handle_photo_message(self, photo_url, msg):
        return self.default_handle_message(msg)

    @abstractmethod
    def default_handle_message(self, msg):
        pass

    @staticmethod
    def _bot_info():
        return 'This is Replika CakeChat telegram bot.'

    def _send_bot_help(self, _):
        help_lines = [self._bot_info(), '', 'List of available commands:']
        for command, (_, description) in self._command_to_handler.items():
            help_lines.append('/{} - {}'.format(command, description))

        return self._send_text('\n'.join(help_lines))

    def handle_command(self, command, arg):
        if command not in self._command_to_handler:
            self._send_text('Unknown command {}'.format(command))
            return self._send_bot_help(arg)

        handler, _ = self._command_to_handler[command]
        return handler(arg)

    def _register_command(self, command, handler, description='???'):
        self._command_to_handler[command] = (handler, description)


class ReversedChatSession(AbstractTelegramChatSession):
    def __init__(self, *args, **kwargs):
        super(ReversedChatSession, self).__init__(*args, **kwargs)
        self._register_command('start', self.greet)
    def greet(self, arg):
        self._send_text('Starting the rocket launch')
    def handle_text_message(self, msg_text, msg):
        self._send_text(msg_text[::-1])
    def default_handle_message(self, msg):
        self._send_text('Sorry, I can only reverse text')


class LaunchFrameXChatSession(AbstractTelegramChatSession):
    def __init__(self, *args, **kwargs):
        super(LaunchFrameXChatSession, self).__init__(*args, **kwargs)
        self._register_command('start', self.greet)
    def greet(self, arg):
        self._send_text('')
    def confirm(self, msg_text, msg):
        message = "Did the rocket launch yet?"
        self._send_text(message)
    def found(self, index, msg):
        message = f"Found! Take-off = {index}"
        self._send_text(message)
    def default_handle_message(self, msg):
        self._send_text('Sorry, I can only reverse text')


class TelegramBot():
    """
    Interface for telegram bot API. Each bot maintains many
    ChatSessions that are handled by classes
    """

    def __init__(self, token):
        """
        :param token: a bot authorization token, can be obtained from the @BotFather bot.
        """
        super(TelegramBot, self).__init__()

        self._token = token
        self._bot = telepot.Bot(token)
        self._chat_id_to_session = {}
        self.my_session = None

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

    def _init_chat_session(self, chat_id, session_class, **session_kwargs):
        session = session_class(self._bot, chat_id, **session_kwargs)
        action = 'Started new' if chat_id not in self._chat_id_to_session else 'Restarted existing'
        """request session"""
        bisector = FrameXBisector(VIDEO_NAME)
        self.my_session = UserSession(chat_id, bisector.count)
        init_frame = int(bisector.count / 2)
        url = get_photo_url(frame=init_frame)
        self._bot.sendPhoto(chat_id, url)
        self._bot.sendMessage(chat_id,f"Init Frame: {init_frame}")
        self._bot.sendMessage(chat_id, "Did it launch yet?")
        return session

    def continue_chat(self, chat_id, left, right, index):
        url = get_photo_url(frame=index)
        self._bot.sendPhoto(chat_id, url)
        self.my_session.update_cookies(launchLeft=left, launchRight=right, launchIndex=index)
        self._bot.sendMessage(chat_id, f"{index} - Did it launch yet?")
        print(index)

    def end_chat(self, chat_id, index):
        url = get_photo_url(frame=index)
        self._bot.sendPhoto(chat_id, url)
        self.my_session.update_cookies(launchLeft=0, launchRight=0, launchIndex=0)
        self.my_session.deactivate(chat_id)
        self._bot.sendMessage(chat_id, f"The rocket was launched on the frame: {index}!")

    def run(self, session_class, **session_kwargs):
        """
        :param session_class: subclass of AbstractTelegramChat
        """

        def _handler(msg):
            content_type, chat_type, chat_id = telepot.glance(msg)

            if chat_id not in self._chat_id_to_session:

                self._chat_id_to_session[chat_id] = self._init_chat_session(chat_id, session_class, **session_kwargs)
                self._chat_id_to_session[chat_id]._send_text("Please enter yes or no.")
                return "Ok"

            session = self._chat_id_to_session[chat_id]

            if content_type == 'text' and msg['text'].startswith('/'):
                command, arg = self._parse_command(msg['text'])
                if command == 'start':
                    session = self._chat_id_to_session[chat_id] = self._init_chat_session(
                        chat_id, session_class, **session_kwargs)
                    session._send_text("Please enter yes or no.")

                return session.handle_command(command, arg)

            if content_type == 'text':
                cookies = self.my_session.get_cookies_json()
                left = int(cookies['launchLeft'])
                right = int(cookies['launchRight'])
                if msg['text'] == "yes":
                    right = int((left + right) / 2)
                    index = int((left + right) / 2)
                    if left + 1 >= right:
                        self.end_chat(chat_id, index)
                    else:
                        self.continue_chat(chat_id, left, right, index)
                elif msg['text'] == "no":
                    left = int((left + right) / 2)
                    index = int((left + right) / 2)
                    if left + 1 >= right:
                        self.end_chat(chat_id, index)
                    else:
                        self.continue_chat( chat_id, left, right, index)
                else:
                    session._send_text("Please enter yes or no.")
                return "ok"

            if content_type == 'photo':
                photo_url = self._extract_photo_url(msg['photo'])
                return session.handle_photo_message(photo_url, msg)


            return session.default_handle_message(msg)

        telepot.loop.MessageLoop(self._bot, _handler).run_forever()


class UserSession():
    """
    Requests session
    """
    def __init__(self, chat_id, launchRight):
        index = int(launchRight / 2)
        self._set_cookie_url = 'https://httpbin.org/cookies/set'
        self._get_cookies_url = 'https://httpbin.org/cookies'
        self.launchStatus = {'launchStatus': "Inactive"}
        self.launchChatID = {'launchChatID': chat_id}
        self.launchRight = {'launchRight': launchRight}
        self.launchLeft = {'launchLeft': 0}
        self.launchIndex = {'launchIndex': index}
        self.session = requests.Session()
        self.session.get(self._set_cookie_url, params=self.launchChatID)
        self.session.get(self._set_cookie_url, params=self.launchRight)
        self.session.get(self._set_cookie_url, params=self.launchLeft)
        self.session.get(self._set_cookie_url, params=self.launchIndex)


    def get_cookies_json(self):
        r = self.session.get(self._get_cookies_url).json()
        return r["cookies"]

    def update_cookies(self, launchLeft, launchRight, launchIndex):
        self.launchRight = {'launchRight': launchRight}
        self.launchLeft = {'launchLeft': launchLeft}
        self.launchIndex = {'launchIndex': launchIndex}

        self.session.get(self._set_cookie_url, params=self.launchChatID)
        self.session.get(self._set_cookie_url, params=self.launchRight)
        self.session.get(self._set_cookie_url, params=self.launchLeft)
        self.session.get(self._set_cookie_url, params=self.launchIndex)

    def deactivate(self, chat_id):
        self.launchStatus = {'launchStatus': "Inactive"}
        self.launchChatID = {'launchChatID': chat_id}
        self.session.get(self._set_cookie_url, params=self.launchStatus)
        self.session.get(self._set_cookie_url, params=self.launchChatID)


#NewToken = "1210920754:AAHEO21N0TL7NnuLbI3ZJ_TmXgPKXkF9ViQ"
#TelegramBot(NewToken).run(ReversedChatSession)
