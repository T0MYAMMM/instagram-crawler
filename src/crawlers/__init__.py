import logging
from urllib.parse import urlparse

import requests
from requests.packages.urllib3.exceptions import InsecureRequestWarning

from crawlers.mixins.account import AccountMixin
from crawlers.mixins.album import DownloadAlbumMixin, UploadAlbumMixin
from crawlers.mixins.auth import LoginMixin
from crawlers.mixins.bloks import BloksMixin
from crawlers.mixins.challenge import ChallengeResolveMixin
from crawlers.mixins.clip import DownloadClipMixin, UploadClipMixin
from crawlers.mixins.collection import CollectionMixin
from crawlers.mixins.comment import CommentMixin
from crawlers.mixins.direct import DirectMixin
from crawlers.mixins.explore import ExploreMixin
from crawlers.mixins.fbsearch import FbSearchMixin
from crawlers.mixins.fundraiser import FundraiserMixin
from crawlers.mixins.hashtag import HashtagMixin
from crawlers.mixins.highlight import HighlightMixin
from crawlers.mixins.igtv import DownloadIGTVMixin, UploadIGTVMixin
from crawlers.mixins.insights import InsightsMixin
from crawlers.mixins.location import LocationMixin
from crawlers.mixins.media import MediaMixin
from crawlers.mixins.multiple_accounts import MultipleAccountsMixin
from crawlers.mixins.note import NoteMixin
from crawlers.mixins.notification import NotificationMixin
from crawlers.mixins.password import PasswordMixin
from crawlers.mixins.photo import DownloadPhotoMixin, UploadPhotoMixin
from crawlers.mixins.private import PrivateRequestMixin
from crawlers.mixins.public import (
    ProfilePublicMixin,
    PublicRequestMixin,
    TopSearchesPublicMixin,
)
from crawlers.mixins.share import ShareMixin
from crawlers.mixins.signup import SignUpMixin
from crawlers.mixins.story import StoryMixin
from crawlers.mixins.timeline import ReelsMixin
from crawlers.mixins.totp import TOTPMixin
from crawlers.mixins.track import TrackMixin
from crawlers.mixins.user import UserMixin
from crawlers.mixins.video import DownloadVideoMixin, UploadVideoMixin

requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

# Used as fallback logger if another is not provided.
DEFAULT_LOGGER = logging.getLogger("crawlers")


class Client(
    PublicRequestMixin,
    ChallengeResolveMixin,
    PrivateRequestMixin,
    TopSearchesPublicMixin,
    ProfilePublicMixin,
    LoginMixin,
    ShareMixin,
    TrackMixin,
    FbSearchMixin,
    HighlightMixin,
    DownloadPhotoMixin,
    UploadPhotoMixin,
    DownloadVideoMixin,
    UploadVideoMixin,
    DownloadAlbumMixin,
    NotificationMixin,
    UploadAlbumMixin,
    DownloadIGTVMixin,
    UploadIGTVMixin,
    MediaMixin,
    UserMixin,
    InsightsMixin,
    CollectionMixin,
    AccountMixin,
    DirectMixin,
    LocationMixin,
    HashtagMixin,
    CommentMixin,
    StoryMixin,
    PasswordMixin,
    SignUpMixin,
    DownloadClipMixin,
    UploadClipMixin,
    ReelsMixin,
    ExploreMixin,
    BloksMixin,
    TOTPMixin,
    MultipleAccountsMixin,
    NoteMixin,
    FundraiserMixin,
):
    proxy = None

    def __init__(
        self,
        settings: dict = {},
        proxy: str = None,
        delay_range: list = None,
        logger=DEFAULT_LOGGER,
        **kwargs,
    ):

        super().__init__(**kwargs)

        self.settings = settings
        self.logger = logger
        self.delay_range = delay_range

        self.set_proxy(proxy)

        self.init()

    def set_proxy(self, dsn: str):
        if dsn:
            assert isinstance(
                dsn, str
            ), f'Proxy must been string (URL), but now "{dsn}" ({type(dsn)})'
            self.proxy = dsn
            proxy_href = "{scheme}{href}".format(
                scheme="http://" if not urlparse(self.proxy).scheme else "",
                href=self.proxy,
            )
            self.public.proxies = self.private.proxies = {
                "http": proxy_href,
                "https": proxy_href,
            }
            return True
        self.public.proxies = self.private.proxies = {}
        return False
