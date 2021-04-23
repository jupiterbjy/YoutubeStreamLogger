"""
Setting this up everytime in interpreter ain't fun. So just import this in interpreter.
Will look for google api from file named `api_key` on cwd, will ask for api if there's
no file.
"""

import pathlib
import datetime
from typing import List, Dict, Any, Tuple, Callable

from dateutil import parser as date_parser
from googleapiclient.discovery import build


YOUTUBE_API_SERVICE = "youtube"
YOUTUBE_API_VERSION = "v3"
API_FILE = pathlib.Path(__file__).parent.joinpath("api_key").absolute()


def build_youtube_resource(api_key=None):
    if api_key is None:
        # if file path is wrong, will raise file not found. handle it outside.
        with open(API_FILE) as _fp:
            api_key = _fp.read()

    youtube = build(YOUTUBE_API_SERVICE, YOUTUBE_API_VERSION, developerKey=api_key)
    return youtube


class Client:
    def __init__(self, api_key=None):
        self.youtube_client = build_youtube_resource(api_key)
        self.video_api = self.youtube_client.videos()
        self.channel_api = self.youtube_client.channels()
        self.search_api = self.youtube_client.search()

    def stream_status(self, video_id) -> str:
        # This is most inefficient out of these methods.. but it's way simpler than first code.

        req = self.video_api.list(
            id=video_id, part="snippet", fields="items/snippet/liveBroadcastContent"
        )
        return req.execute()["items"][0]["snippet"]["liveBroadcastContent"]

    def get_video_title(self, video_id) -> str:
        req = self.video_api.list(
            id=video_id, part="snippet", fields="items/snippet/title"
        )
        return req.execute()["items"][0]["snippet"]["title"]

    def get_channel_id(self, video_id) -> str:
        req = self.video_api.list(
            id=video_id, part="snippet", fields="items/snippet/channelId"
        )
        return req.execute()["items"][0]["snippet"]["channelId"]

    def get_subscribers_count(self, channel_id) -> Callable:
        req = self.channel_api.list(
            id=channel_id,
            part="statistics",
            fields="items/statistics/subscriberCount",
        )
        return req.execute()["items"][0]["statistics"]["subscriberCount"]

    def check_upcoming(self, channel_id: str) -> Tuple[str, ...]:
        req = self.search_api.list(
            channelId=channel_id, part="snippet", type="video", eventType="upcoming"
        )
        items = req.execute()["items"]
        return tuple(item["id"]["videoId"] for item in items)

    def check_live(self, channel_id: str) -> Tuple[str, ...]:
        req = self.search_api.list(
            channelId=channel_id, part="snippet", type="video", eventType="live"
        )
        items = req.execute()["items"]
        return tuple(item["id"]["videoId"] for item in items)

    def get_start_time(self, video_id) -> datetime.datetime:
        req = self.video_api.list(
            id=video_id,
            part="liveStreamingDetails",
            fields="items/liveStreamingDetails/scheduledStartTime",
        )
        time_string = req.excute()["items"][0]["liveStreamingDetails"][
            "scheduledStartTime"
        ]

        start_time = date_parser.isoparse(time_string)
        return start_time