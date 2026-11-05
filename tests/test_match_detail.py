from datetime import datetime, timedelta, timezone

import pytest

from tests.apiError import assert_api_error

KST = timezone(timedelta(hours=9))
MATCHTYPE = 50
DETAIL_COUNT = 10
NORMAL_END = 0
FORFEIT_WIN = 1
FORFEIT_LOSS = 2

@pytest.fixture(scope="module")
def match_ids(client, ouid):
    response = client.get_user_matches(ouid, MATCHTYPE, 0, DETAIL_COUNT)
    assert response.status_code == 200, f"매치 기록 조회 실패: {response.status_code} {response.text}"
    ids = response.json()
    assert len(ids) > 0, "공식 경기 기록이 없는 계정입니다 (테스트 데이터 전제 조건)"
    return ids


@pytest.fixture(scope="module")
def match_details(client, match_ids):
    details = []
    for match_id in match_ids:
        response = client.get_match_detail(match_id)
        assert response.status_code == 200, f"매치 상세 조회 실패 ({match_id}): {response.status_code} {response.text}"
        details.append(response.json())
    return details


@pytest.fixture(scope="module")
def normal_matches(match_details):
    normal = []
    for d in match_details:
        if len(d["matchInfo"]) == 2 and all(m["matchDetail"]["matchEndType"] == NORMAL_END for m in d["matchInfo"]):
            normal.append(d)
    assert len(normal) > 0, f"최근 {len(match_details)}경기 중 정상 종료된 경기가 없습니다 (테스트 데이터 전제 조건)"
    return normal


@pytest.fixture(scope="module")
def forfeit_matches(match_details):
    forfeit = []
    for d in match_details:
        if any(m["matchDetail"]["matchEndType"] != NORMAL_END for m in d["matchInfo"]):
            forfeit.append(d)
    # 몰수 경기는 드물게 발생하므로, 조회 범위에 없으면 실패가 아니라 건너뜁니다.
    if not forfeit:
        pytest.skip(f"최근 {len(match_details)}경기 중 몰수 경기가 없어 검증할 수 없습니다")
    return forfeit


class TestMatchDetail:
    def test_매치_상세_조회(self, client, ouid, match_ids):
        match_id = match_ids[0]
        response = client.get_match_detail(match_id)
        assert response.status_code == 200, f"매치 상세 조회 실패: {response.status_code} {response.text}"
        detail = response.json()
        assert detail["matchId"] == match_id, f"요청한 matchId와 응답의 matchId가 다릅니다: {detail['matchId']}"
        assert detail["matchType"] == MATCHTYPE, f"공식 경기({MATCHTYPE})가 아닌 matchType이 반환되었습니다: {detail['matchType']}"
        assert len(detail["matchInfo"]) == 2, f"1:1 경기인데 참가자 정보가 {len(detail['matchInfo'])}개입니다"
        participants = [m["ouid"] for m in detail["matchInfo"]]
        assert ouid in participants, "조회한 유저가 매치 참가자 목록에 없습니다"

    def test_매치_날짜_정상_확인(self, match_details):
        now = datetime.now(KST)
        for d in match_details:
            date_str = d["matchDate"]
            try:
                played = datetime.fromisoformat(date_str)
            except (TypeError, ValueError):
                pytest.fail(f"매치 {d['matchId']}의 경기 날짜 형식이 잘못되었습니다: {date_str!r}")

            played = played.replace(tzinfo=KST)
            assert played <= now, f"매치 {d['matchId']}의 경기 날짜가 미래입니다: {date_str}"

    def test_정상_매치_결과_확인(self, normal_matches):
        for d in normal_matches:
            player1, player2 = d["matchInfo"]
            result_player1, result_player2 = player1["matchDetail"]["matchResult"], player2["matchDetail"]["matchResult"]
            score_player1, score_player2 = player1["shoot"]["goalTotalDisplay"], player2["shoot"]["goalTotalDisplay"]
            shootout_player1, shootout_player2 = player1["shoot"]["shootOutScore"], player2["shoot"]["shootOutScore"]
            is_shootout = shootout_player1 > 0 or shootout_player2 > 0

            # 득점이 같고 승부차기를 했다면 승부차기 점수로 판정합니다.
            if score_player1 == score_player2 and is_shootout:
                score_player1, score_player2 = shootout_player1, shootout_player2

            if score_player1 == score_player2:
                expected = ("무", "무")
            elif score_player1 > score_player2:
                expected = ("승", "패")
            else:
                expected = ("패", "승")
            assert (result_player1, result_player2) == expected, (
                f"매치 {d['matchId']}의 승패가 득점과 맞지 않습니다: "
                f"결과 {result_player1}:{result_player2}, 득점 {player1['shoot']['goalTotalDisplay']}:{player2['shoot']['goalTotalDisplay']}, "
                f"승부차기 {player1['shoot']['shootOutScore']}:{player2['shoot']['shootOutScore']}"
            )

    def test_몰수_매치_결과_확인(self, forfeit_matches):
        # matchEndType: 0 정상종료, 1 몰수승, 2 몰수패
        expected_result = {FORFEIT_WIN: "승", FORFEIT_LOSS: "패"}
        for d in forfeit_matches:
            end_types = sorted(m["matchDetail"]["matchEndType"] for m in d["matchInfo"])
            assert end_types == [FORFEIT_WIN, FORFEIT_LOSS], (
                f"매치 {d['matchId']}: 몰수 경기는 한쪽이 몰수승(1), 다른 쪽이 몰수패(2)여야 합니다: {end_types}"
            )

            for m in d["matchInfo"]:
                end_type = m["matchDetail"]["matchEndType"]
                result = m["matchDetail"]["matchResult"]
                assert result == expected_result[end_type], (
                    f"매치 {d['matchId']}: matchEndType {end_type}인데 결과가 {result}입니다 (기대 {expected_result[end_type]})"
                )

    def test_슈팅과_골_기록이_일치한다(self, normal_matches):
        for d in normal_matches:
            for m in d["matchInfo"]:
                shoot = m["shoot"]
                shoot_details = len(m["shootDetail"])
                player_goals = sum(p["status"]["goal"] for p in m["player"])
                assert shoot_details == shoot["shootTotal"], (
                    f"매치 {d['matchId']}: 슈팅 상세 {shoot_details}건과 shootTotal {shoot['shootTotal']}이 다릅니다"
                )
                assert player_goals == shoot["goalTotal"], (
                    f"매치 {d['matchId']}: 선수별 골 합계 {player_goals}와 goalTotal {shoot['goalTotal']}이 다릅니다"
                )

    def test_매치_정보는_메타데이터에_존재한다(self, match_details, matchtype_meta, division_meta):
        valid_match_types = {m["matchtype"] for m in matchtype_meta}
        valid_divisions = {d["divisionId"] for d in division_meta}
        invalid_types = [d["matchType"] for d in match_details if d["matchType"] not in valid_match_types]
        invalid_divisions = [m["division"] for d in match_details for m in d["matchInfo"] if m["division"] not in valid_divisions]
        assert not invalid_types, f"매치 종류 메타데이터에 없는 matchType: {invalid_types}"
        assert not invalid_divisions, f"등급 메타데이터에 없는 division: {invalid_divisions}"

    @pytest.mark.parametrize("matchid", [
        "wrong_matchid",               # 형식이 잘못된 matchid
        "000000000000000000000000",    # 형식은 맞지만 존재하지 않는 matchid
        None,                          # matchid 파라미터 없음
    ])
    def test_예외처리_매치_상세_조회(self, client, matchid):
        response = client.get_match_detail(matchid)
        assert response.status_code == 400, f"{response.status_code} {response.text}"
        assert_api_error(response.json(), "OPENAPI00004", "Please input valid parameter")
