from datetime import datetime

import pytest

from tests.apiError import assert_api_error


class TestTrade:
    def test_거래한_선수_메타데이터에_존재한다(self, client, spid_meta):
        response = client.get_user_trades("buy", 0, 5)
        assert response.status_code == 200, f"거래 기록 조회 실패: {response.status_code} {response.text}"
        trades = response.json()
        assert len(trades) > 0, "buy 거래 기록이 없는 계정입니다 (테스트 데이터 전제 조건)"

        valid_spids = {p["id"] for p in spid_meta}
        for t in trades:
            assert t["spid"] in valid_spids, f"거래한 선수 {t['spid']}가 선수 메타데이터에 없습니다."

    @pytest.mark.parametrize("tradetype", ["buy", "sell"])
    def test_유저_거래_정렬_확인(self, client, tradetype):
        response = client.get_user_trades(tradetype, 0, 100)
        assert response.status_code == 200, f"{tradetype} 거래 기록 조회 실패: {response.status_code} {response.text}"
        trades = response.json()
        assert len(trades) >= 2, f"{tradetype} 거래 기록이 {len(trades)}건이라 정렬을 확인할 수 없습니다"
        dates = [datetime.fromisoformat(t["tradeDate"]) for t in trades]
        assert dates == sorted(dates, reverse=True), f"{tradetype} 거래 기록이 최신 거래부터 내림차순으로 정렬되어 있지 않습니다"

    @pytest.mark.parametrize("offset, limit", [
        (0, 0),
        (0, 101),
        (-1, 10),
    ])
    def test_유저_거래_조회_경계값(self, client, offset, limit):
        response = client.get_user_trades("buy", offset, limit)
        assert response.status_code == 400, f"{response.status_code} {response.text}"
        assert_api_error(response.json(), "OPENAPI00004", "Please input valid parameter")

    @pytest.mark.parametrize("tradetype", ["wrong_tradetype", None])
    def test_예외처리_유저_거래_조회(self, client, tradetype):
        response = client.get_user_trades(tradetype, 0, 5)
        assert response.status_code == 400, f"{response.status_code} {response.text}"
        assert_api_error(response.json(), "OPENAPI00004", "Please input valid parameter")
