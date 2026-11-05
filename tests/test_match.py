import pytest

from tests.apiError import assert_api_error

MATCHTYPE = 50


class TestMatch:
    def test_유저_1경기만_조회(self, client, ouid):
        response = client.get_user_matches(ouid, MATCHTYPE, 0, 1)
        assert response.status_code == 200, f"매치 기록 조회 실패: {response.status_code} {response.text}"
        matches = response.json()
        assert len(matches) == 1, f"1경기를 요청했지만 {len(matches)}경기가 반환되었습니다"

    def test_유저_최대경기_조회(self, client, ouid):
        response = client.get_user_matches(ouid, MATCHTYPE, 0, 100)
        assert response.status_code == 200, f"매치 기록 조회 실패: {response.status_code} {response.text}"
        matches = response.json()
        assert len(matches) == 100, f"유저의 총 매치수가 100경기보다 적습니다."

    @pytest.mark.parametrize("limit", [0, 101])
    def test_경계값_매치수(self, client, ouid, limit):
        response = client.get_user_matches(ouid, MATCHTYPE, 0, limit)
        assert response.status_code == 400, f"{response.status_code} {response.text}"
        assert_api_error(response.json(), "OPENAPI00004", "Please input valid parameter")
