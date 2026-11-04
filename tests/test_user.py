import pytest

from conftest import TEST_NICKNAME
from tests.apiError import assert_api_error
from datetime import datetime, timedelta, timezone

KST = timezone(timedelta(hours=9))

class TestUser :
    def test_유저_ouid_조회(self,client) :
        response = client.get_ouid(TEST_NICKNAME)
        assert response.status_code == 200
        data = response.json()
        assert type(data['ouid']) is str

    def test_유저_정보_조회(self,client,ouid) :
        response = client.get_user_basic(ouid) 
        assert response.status_code == 200
        user = response.json()
        assert type(user['nickname']) is str
        assert type(user['level']) is int
        assert user['level'] >= 1
        assert user['ouid'] == ouid
        assert user['nickname'] == TEST_NICKNAME

    def test_최고등급의_매치종류는_메타데이터에_존재한다(self, max_divisions, matchtype_meta):
        valid_match_types = {m["matchtype"] for m in matchtype_meta}
        assert all(d["matchType"] in valid_match_types for d in max_divisions)

    def test_최고등급의_등급값은_메타데이터에_존재한다(self, max_divisions, division_meta):
        valid_divisions = {d["divisionId"] for d in division_meta}
        assert all(d["division"] in valid_divisions for d in max_divisions)

    def test_최고등급_달성_정상_날짜_확인(self,max_divisions):
        now = datetime.now(KST)
        for d in max_divisions:
            date_str = d["achievementDate"]
            try:
                achieved = datetime.fromisoformat(date_str)
            except (TypeError, ValueError):
                pytest.fail(f"매치 종류 {d['matchType']}의 달성일 형식이 잘못되었습니다: {date_str!r}") 

            achieved = achieved.replace(tzinfo=KST) 
            assert achieved <= now, f"매치 종류 {d['matchType']}의 달성일이 미래입니다: {date_str}"
            
    @pytest.mark.parametrize("nickname", ['wrong_nickname', None])
    def test_예외처리_닉네임(self, client,nickname) :
        response = client.get_ouid(nickname)
        assert response.status_code == 400
        res = response.json()
        assert_api_error(res,"OPENAPI00004", "Please input valid parameter")

    def test_잘못된_ouid(self,client) :
        response = client.get_user_basic('wrong_ouid')
        assert response.status_code == 400
        res = response.json()
        assert_api_error(res,"OPENAPI00003", "Please input valid id")
