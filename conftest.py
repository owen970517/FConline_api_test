import os

import pytest
from dotenv import load_dotenv

from api_client import FcOnlineClient

load_dotenv()  # .env 파일 읽어서 등록
BASE_URL = os.getenv("API_BASE_URL", "https://open.api.nexon.com")
API_KEY = os.getenv("NEXON_API_KEY")  # API_KEY 등록
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


@pytest.fixture(scope="session")
def matchtype_meta(client):
    response = client.get_meta("matchtype")
    assert response.status_code == 200, f"매치 종류 메타데이터 조회 실패: {response.status_code} {response.text}"
    return response.json()


@pytest.fixture(scope="session")
def division_meta(client):
    response = client.get_meta("division")
    assert response.status_code == 200, f"등급 메타데이터 조회 실패: {response.status_code} {response.text}"
    return response.json()


@pytest.fixture(scope="session")
def spid_meta(client):
    response = client.get_meta("spid")
    assert response.status_code == 200, f"선수 메타데이터 조회 실패: {response.status_code} {response.text}"
    return response.json()


@pytest.fixture(scope="session")
def max_divisions(client, ouid):
    response = client.get_user_max_division(ouid)
    assert response.status_code == 200, f"최고 등급 조회 실패: {response.status_code} {response.text}"
    data = response.json()
    assert len(data) > 0, "최고 등급 기록이 없는 계정입니다 (테스트 데이터 전제 조건)"
    return data
