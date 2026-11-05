from datetime import datetime, timedelta, timezone

import pytest

from conftest import TEST_NICKNAME
from tests.apiError import assert_api_error

KST = timezone(timedelta(hours=9))


class TestUser:
    def test_유저_ouid_조회(self, client):
        response = client.get_ouid(TEST_NICKNAME)
        assert response.status_code == 200, f"ouid 조회 실패: {response.status_code} {response.text}"
        data = response.json()
        assert type(data["ouid"]) is str, f"ouid가 문자열이 아닙니다: {data['ouid']!r}"

    def test_유저_정보_조회(self, client, ouid):
        response = client.get_user_basic(ouid)
        assert response.status_code == 200, f"유저 정보 조회 실패: {response.status_code} {response.text}"
        user = response.json()
        assert type(user["nickname"]) is str, f"nickname이 문자열이 아닙니다: {user['nickname']!r}"
        assert type(user["level"]) is int, f"level이 정수가 아닙니다: {user['level']!r}"
        assert user["level"] >= 1, f"level이 1보다 작습니다: {user['level']}"
        assert user["ouid"] == ouid, f"요청한 ouid와 응답의 ouid가 다릅니다: {user['ouid']}"
        assert user["nickname"] == TEST_NICKNAME, f"요청한 닉네임과 응답의 닉네임이 다릅니다: {user['nickname']}"

    def test_최고등급의_매치종류는_메타데이터에_존재한다(self, max_divisions, matchtype_meta):
        valid_match_types = {m["matchtype"] for m in matchtype_meta}
        invalid = [d["matchType"] for d in max_divisions if d["matchType"] not in valid_match_types]
        assert not invalid, f"매치 종류 메타데이터에 없는 matchType: {invalid}"

    def test_최고등급의_등급값은_메타데이터에_존재한다(self, max_divisions, division_meta):
        valid_divisions = {d["divisionId"] for d in division_meta}
        invalid = [d["division"] for d in max_divisions if d["division"] not in valid_divisions]
        assert not invalid, f"등급 메타데이터에 없는 division: {invalid}"

    def test_최고등급_달성_정상_날짜_확인(self, max_divisions):
        now = datetime.now(KST)
        for d in max_divisions:
            date_str = d["achievementDate"]
            try:
                achieved = datetime.fromisoformat(date_str)
            except (TypeError, ValueError):
                pytest.fail(f"매치 종류 {d['matchType']}의 달성일 형식이 잘못되었습니다: {date_str!r}")

            achieved = achieved.replace(tzinfo=KST)
            assert achieved <= now, f"매치 종류 {d['matchType']}의 달성일이 미래입니다: {date_str}"

    @pytest.mark.parametrize("nickname", ["wrong_nickname", None])
    def test_예외처리_닉네임(self, client, nickname):
        response = client.get_ouid(nickname)
        assert response.status_code == 400, f"{response.status_code} {response.text}"
        assert_api_error(response.json(), "OPENAPI00004", "Please input valid parameter")

    def test_잘못된_ouid(self, client):
        response = client.get_user_basic("wrong_ouid")
        assert response.status_code == 400, f"{response.status_code} {response.text}"
        assert_api_error(response.json(), "OPENAPI00003", "Please input valid id")
