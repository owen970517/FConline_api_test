import pytest

from conftest import TEST_NICKNAME
from tests.apiError import assert_api_error

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
