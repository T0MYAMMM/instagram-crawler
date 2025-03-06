from requests import Response


class HTTPStatusException(Exception):
    def __init__(self, status, message="", url=None, resp: Response = None):
        self.status = status
        self.message = 'HTTP Status: {} - {}'.format(status, message)
        self.url = url
        self.response = resp
        super().__init__(self.message)


class InvalidCookieException(Exception):
    def __init__(self, resource_id, message="", url=None):
        self.message = 'Invalid Cookie: {} - {}'.format(resource_id, message)
        self.url = url
        super().__init__(self.message)


class NoAvailableResourceException(Exception):
    def __init__(self, social_media, allowed_usage, message=""):
        self.message = 'No Available Resource: {} - {}'.format(
            social_media, allowed_usage)
        super().__init__(self.message)


class InstagramError(Exception):
    def __init__(self, code, message="", url=None, resp: Response = None):
        self.code = code
        self.message = message
        self.url = url
        self.response = resp
        super().__init__(self.message)


class GoogleMapsError(Exception):
    def __init__(self, message=""):
        self.message = message
        super().__init__(self.message)


class TiktokError(Exception):
    def __init__(self, status_code, message=""):
        self.message = message
        self.status_code = status_code
        super().__init__(self.message)