import io
import os
from typing import List, NamedTuple, Text
from urllib.parse import quote, urljoin

import pygame
from httpx import Client
from PIL import Image

API_BASE = os.getenv("API_BASE", "https://framex-dev.wadrid.net/api/")
VIDEO_NAME = os.getenv(
    "VIDEO_NAME", "Falcon Heavy Test Flight (Hosted Webcast)-wbSwFU6tY1c"
)

def get_photo_frame(frame):
    new_client = Client()
    res = new_client.get(urljoin(API_BASE, f'video/{quote(VIDEO_NAME)}/frame/{quote(f"{frame}")}/'))
    return res

def get_photo_url(frame):
    url = urljoin(API_BASE, f'video/{quote(VIDEO_NAME)}/frame/{quote(f"{frame}")}/')
    return url
"""
def get_video_count(video):
    new_client = Client()
    r = new_client.get(urljoin(self.BASE_URL, f"video/{quote(video)}/"))
    return url
"""


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
"""
bisector = FrameXBisector(VIDEO_NAME)
print(f"bisector count: {bisector.count}")
import telepot
bot = telepot.Bot("1210920754:AAHEO21N0TL7NnuLbI3ZJ_TmXgPKXkF9ViQ")
id = 1015798095 #id Thibaut
chat_id = -424370076
url_frame = get_photo_url(bisector.count)
bot.sendMessage(id, f"Frame: {bisector.count}")
print()
bot.sendPhoto(id, url_frame)

index = bisector.count / 2
url_frame = get_photo_url(index)
bot.sendMessage(id, f"Frame: {index}")
bot.sendPhoto(id, url_frame)
"""
