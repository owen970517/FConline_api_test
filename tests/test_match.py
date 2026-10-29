import pytest

from tests.apiError import assert_api_error
MATCHTYPE = 50

class TestMatch :
    def test_유저_1경기만_조회(self,client,ouid) :
        response = client.get_user_matches(ouid,MATCHTYPE,0,1)
        assert response.status_code == 200
        matches = response.json()
        assert len(matches) == 1

    def test_유저_최대경기_조회(self,client,ouid) :
        response = client.get_user_matches(ouid,MATCHTYPE,0,100)
        assert response.status_code == 200
        matches = response.json()
        assert len(matches) == 100

    @pytest.mark.parametrize("limit", [0, 101])
    def test_경계값_매치수(self, client,ouid,limit):
        response = client.get_user_matches(ouid,MATCHTYPE,0,limit)
        assert response.status_code == 400
        res = response.json()
        assert_api_error(res,"OPENAPI00004", "Please input valid parameter")