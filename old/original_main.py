import io
import os
from typing import List, NamedTuple, Text
from urllib.parse import quote, urljoin

import pygame
from httpx import Client
from PIL import Image
from PyInquirer import prompt

API_BASE = os.getenv("API_BASE", "https://framex-dev.wadrid.net/api/")
VIDEO_NAME = os.getenv(
    "VIDEO_NAME", "Falcon Heavy Test Flight (Hosted Webcast)-wbSwFU6tY1c"
)

import telepot
bot = telepot.Bot("1210920754:AAHEO21N0TL7NnuLbI3ZJ_TmXgPKXkF9ViQ")
id = 1015798095 #id Thibaut
chat_id = -424370076

class Size(NamedTuple):
    """
    Represents a size
    """

    width: int
    height: int


class Color(NamedTuple):
    """
    8-bit components of a color
    """

    r: int
    g: int
    b: int


class Video(NamedTuple):
    """
    That's a video from the API
    """

    name: Text
    width: int
    height: int
    frames: int
    frame_rate: List[int]
    url: Text
    first_frame: Text
    last_frame: Text


DISPLAY_SIZE = Size(int(480 * 1.5), int(270 * 1.5))
BLACK = Color(0, 0, 0)


def bisect(n, mapper, tester):
    """
    Runs a bisection.

    - `n` is the number of elements to be bisected
    - `mapper` is a callable that will transform an integer from "0" to "n"
      into a value that can be tested
    - `tester` returns true if the value is within the "right" range
    """

    if n < 1:
        raise ValueError("Cannot bissect an empty array")

    left = 0
    print(left)
    print("left: %i" % left)
    right = n - 1
    print("right: %i" % right)

    while left + 1 < right:
        mid = int((left + right) / 2)

        val = mapper(mid)

        if tester(val):
            right = mid
            print("right: %f" % right)

        else:
            left = mid
            print("left: %f" % left)

    return mapper(right)


class Frame:
    """
    Wrapper around frame data to help drawing it on the screen
    """

    def __init__(self, data):
        self.data = data
        self.image = None

    def blit(self, disp):
        if not self.image:
            pil_img = Image.open(io.BytesIO(self.data))
            pil_img.thumbnail(DISPLAY_SIZE)
            buf = pil_img.tobytes()
            size = pil_img.width, pil_img.height
            self.image = pygame.image.frombuffer(buf, size, "RGB")

        disp.blit(self.image, (0, 0))


class FrameX:
    """
    Utility class to access the FrameX API
    """

    BASE_URL = API_BASE

    def __init__(self):
        self.client = Client()

    def video(self, video: Text) -> Video:
        """
        Fetches information about a video
        """

        r = self.client.get(urljoin(self.BASE_URL, f"video/{quote(video)}/"))
        r.raise_for_status()
        return Video(**r.json())

    def video_frame(self, video: Text, frame: int) -> bytes:
        """
        Fetches the JPEG data of a single frame
        """

        r = self.client.get(
            urljoin(self.BASE_URL, f'video/{quote(video)}/frame/{quote(f"{frame}")}/')
        )
        r.raise_for_status()
        return r.content

    def video_url(self, video: Text, frame: int) -> bytes:
        """
        Fetches the URL of a single frame
        """

        r = self.client.get(
            urljoin(self.BASE_URL, f'video/{quote(video)}/frame/{quote(f"{frame}")}/')
        )
        r.raise_for_status()
        return r


class FrameXBisector:
    """
    Helps managing the display of images from the launch
    """

    BASE_URL = API_BASE

    def __init__(self, name):
        self.api = FrameX()
        self.video = self.api.video(name)
        self._index = 0
        self.image = None

    @property
    def index(self):
        return self._index

    @index.setter
    def index(self, v):
        """
        When a new index is written, download the new frame
        """

        self._index = v
        self.image = Frame(self.api.video_frame(self.video.name, v))
        bot.sendPhoto(id, self.api.video_url(self.video.name, v))

    @property
    def count(self):
        return self.video.frames

    def blit(self, disp):
        """
        Draws the current picture.
        """

        self.image.blit(disp)


def confirm(title):
    """
    Asks a yes/no question to the user
    """

    return prompt(
        [
            {
                "type": "confirm",
                "name": "confirm",
                "message": f"{title} - did the rocket launch yet?",
            }
        ]
    )["confirm"]


def main():
    """
    Runs a bisection algorithm on the frames of the video, the goal is
    to figure at which exact frame the rocket takes off.

    Images are displayed using pygame, but the interactivity happens in
    the terminal as it is much easier to do.
    """

    pygame.init()

    bisector = FrameXBisector(VIDEO_NAME)
    disp = pygame.display.set_mode(DISPLAY_SIZE)
    #disp = bot.sendPhoto(id, URL)

    def mapper(n):
        """
        In that case there is no need to map (or rather, the mapping
        is done visually by the user)
        """

        return n

    def tester(n):
        """
        Displays the current candidate to the user and asks them to
        check if they see wildfire damages.
        """

        bisector.index = n
        disp.fill(BLACK)
        bisector.blit(disp)
        pygame.display.update()

        return confirm(bisector.index)

    culprit = bisect(bisector.count, mapper, tester)
    bisector.index = culprit

    print(f"Found! Take-off = {bisector.index}")

    pygame.quit()
    exit()

"""
from telepot.loop import MessageLoop
def handle(msg):
    chat_id = msg['chat']['id']
    command = msg['text']
    #print 'Got command: %s' % command
    if command == 'test_launch':
        bot.sendMessage(id, "Starting t")
        main()
    elif command == 'photo':
        bot.sendPhoto(id, URL)
    else:
        bot.sendMessage(id, "I don't understand")

MessageLoop(bot, handle).run_as_thread()

"""
if __name__ == "__main__":
    main()
