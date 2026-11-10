import time

import requests


class RateLimitError(Exception):
    """재시도 후에도 호출량 제한(429)이 풀리지 않을 때 발생합니다."""


class FcOnlineClient:
    # 모든 클라이언트 인스턴스가 같은 호출 한도를 공유하므로 마지막 요청 시각도 클래스 단위로 관리합니다.
    _last_request_at = 0.0

    def __init__(self, base_url: str, api_key: str | None, timeout: int = 10,
                 min_interval: float = 0.25, max_retries: int = 3):
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self.min_interval = min_interval  # 요청 사이 최소 간격(초)
        self.max_retries = max_retries    # 429를 받았을 때 다시 시도하는 횟수
        self.session = requests.Session()
        if api_key is not None:
            self.session.headers.update({"x-nxopen-api-key": api_key})

    def _wait_for_interval(self):
        elapsed = time.monotonic() - FcOnlineClient._last_request_at
        if elapsed < self.min_interval:
            time.sleep(self.min_interval - elapsed)
        FcOnlineClient._last_request_at = time.monotonic()

    def _get(self, path: str, params: dict | None = None):
        url = f"{self.base_url}{path}"
        for attempt in range(self.max_retries + 1):
            self._wait_for_interval()
            response = self.session.get(url, params=params, timeout=self.timeout)
            if response.status_code != 429:
                return response
            if attempt < self.max_retries:
                # 서버가 Retry-After 헤더를 보내지 않으므로 1초, 2초, 4초로 늘려 가며 기다립니다.
                time.sleep(2 ** attempt)
        raise RateLimitError(
            f"호출 한도 초과: {self.max_retries}번 재시도 후에도 429를 받았습니다. "
            f"하루 호출 한도를 모두 썼을 수 있습니다. ({path}) {response.text}"
        )

    def get_ouid(self, nickname: str):
        return self._get("/fconline/v1/id", params={"nickname": nickname})

    def get_user_basic(self, ouid: str):
        return self._get("/fconline/v1/user/basic", params={"ouid": ouid})

    def get_user_max_division(self, ouid: str):
        return self._get("/fconline/v1/user/maxdivision", params={"ouid": ouid})

    def get_user_trades(self, tradetype: str, offset: int | None = None, limit: int | None = None):
        return self._get("/fconline/v1/user/trade", params={"tradetype": tradetype, "offset": offset, "limit": limit})

    def get_meta(self, meta_name: str):
        return self._get(f"/static/fconline/meta/{meta_name}.json")

    def get_user_matches(self, ouid: str, matchtype: int, offset: int | None = None, limit: int | None = None):
        return self._get("/fconline/v1/user/match", params={"ouid": ouid, "matchtype": matchtype, "offset": offset, "limit": limit})

    def get_match_detail(self, matchid: str):
        return self._get("/fconline/v1/match-detail", params={"matchid": matchid})
