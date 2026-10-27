import requests

class FcOnlineClient:
    def __init__(self, base_url: str, api_key:str | None, timeout: int = 10):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.session = requests.Session()
        if api_key is not None:
            self.session.headers.update({"x-nxopen-api-key": api_key})

    def get_ouid(self, nickname:str):
        return self.session.get(f"{self.base_url}/fconline/v1/id", params={"nickname" : nickname}, timeout=self.timeout)

    def get_user_basic(self, ouid:str):
        return self.session.get(f"{self.base_url}/fconline/v1/user/basic",params={"ouid" : ouid},  timeout=self.timeout)

    def get_meta_data(self):
        return self.session.get(f"{self.base_url}/static/fconline/meta/matchtype.json",  timeout=self.timeout)

    def get_user_matches(self, ouid: str, matchtype: int, offset: int | None = None, limit: int | None = None):
        return self.session.get(f"{self.base_url}/fconline/v1/user/match", params={"ouid" : ouid , "matchtype" : matchtype , "offset" : offset , "limit" : limit} , timeout=self.timeout)