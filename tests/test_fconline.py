import pytest

from conftest import BASE_URL,TEST_NICKNAME
from api_client import FcOnlineClient
def assert_api_error(res, name, message):
    assert res['error']['name'] == name
    assert res['error']['message'] == message

matchtype = 50

class TestGetFConline:
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

    def test_키없이_메타데이터_조회(self):
        no_key_client = FcOnlineClient(BASE_URL, None)
        response = no_key_client.get_meta_data()
        assert response.status_code == 200
        meta = response.json()
        assert len(meta) > 0
        assert type(meta[0]['matchtype']) is int
        assert type(meta[0]['desc']) is str

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

    @pytest.mark.parametrize("api_key, expected_name, expected_message", [
        ("wrong-key", "OPENAPI00005", "The apikey is not valid."),       # TC-11
        (None,        "OPENAPI00004", "Please input valid parameter"),   # TC-12
        ("",          "OPENAPI00004", "Please input valid parameter"),   # TC-13
    ])
    def test_잘못되거나_없는_키는_거부된다(self, api_key, expected_name, expected_message):
        bad_client = FcOnlineClient(BASE_URL, api_key)
        response = bad_client.get_ouid(TEST_NICKNAME)
        assert response.status_code == 400
        assert_api_error(response.json(), expected_name, expected_message)

class TestGetBVAFConline:
    def test_유저_1경기만_조회(self,client,ouid) :
        response = client.get_user_matches(ouid,matchtype,0,1)
        assert response.status_code == 200
        matches = response.json()
        assert len(matches) == 1

    def test_유저_최대경기_조회(self,client,ouid) :
        response = client.get_user_matches(ouid,matchtype,0,100)
        assert response.status_code == 200
        matches = response.json()
        assert len(matches) == 100

    @pytest.mark.parametrize("limit", [0, 101])
    def test_경계값_매치수(self, client,ouid,limit):
        response = client.get_user_matches(ouid,matchtype,0,limit)
        assert response.status_code == 400
        res = response.json()
        assert_api_error(res,"OPENAPI00004", "Please input valid parameter")
