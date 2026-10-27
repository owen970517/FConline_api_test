import os

import pytest

from api_client import FcOnlineClient
from dotenv import load_dotenv

load_dotenv() #.env 파일 읽어서 등록
BASE_URL = os.getenv("API_BASE_URL", "https://open.api.nexon.com")
API_KEY = os.getenv("NEXON_API_KEY") # API_KEY 등록
TEST_NICKNAME = os.getenv("TEST_NICKNAME")
@pytest.fixture(scope="session")
def client():
    if API_KEY is None:
        pytest.fail("NEXON_API_KEY 환경변수가 설정되지 않았습니다")
    return FcOnlineClient(BASE_URL, API_KEY)

@pytest.fixture(scope="session")
def ouid(client):
    if TEST_NICKNAME is None:
        pytest.fail("TEST_NICKNAME 환경변수가 설정되지 않았습니다")
    response = client.get_ouid(TEST_NICKNAME)
    assert response.status_code == 200, f"ouid 조회 실패: {response.status_code} {response.text}"
    data = response.json()
    return data["ouid"]

