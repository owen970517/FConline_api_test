"""게임 정기 점검 중 API 응답을 기록하는 확인용 스크립트입니다 (테스트가 아님).

엔드포인트마다 한 번씩 호출해 상태 코드와 에러 코드를 표로 출력합니다.
점검 응답이 와도 실패로 처리하지 않고 항상 정상 종료합니다.
GitHub Actions에서 실행하면 결과 표를 Job Summary에도 남깁니다.

실행: python scripts/maintenance_check.py
"""
import os
import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

from dotenv import load_dotenv

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))
from api_client import FcOnlineClient, RateLimitError  # noqa: E402

KST = timezone(timedelta(hours=9))
MATCHTYPE = 50


def describe(response):
    if response is None:
        return "-", "-", "앞 단계 실패로 호출하지 않음"
    try:
        body = response.json()
    except ValueError:
        return response.status_code, "-", response.text[:80]
    if isinstance(body, dict) and isinstance(body.get("error"), dict):
        return response.status_code, body["error"].get("name", "-"), body["error"].get("message", "-")
    return response.status_code, "-", "정상 응답"


def call(name, func, *args, **kwargs):
    try:
        return func(*args, **kwargs)
    except RateLimitError as e:
        print(f"[{name}] {e}")
        return None


def main():
    sys.stdout.reconfigure(encoding="utf-8") 
    load_dotenv()
    client = FcOnlineClient(os.getenv("API_BASE_URL", "https://open.api.nexon.com"), os.getenv("NEXON_API_KEY"))
    nickname = os.getenv("TEST_NICKNAME")
    results = []

    r = call("/id", client.get_ouid, nickname)
    results.append(("/id", r))
    ouid = r.json().get("ouid") if r is not None and r.status_code == 200 else None

    for name, func in [
        ("/user/basic", client.get_user_basic),
        ("/user/maxdivision", client.get_user_max_division),
    ]:
        results.append((name, call(name, func, ouid) if ouid else None))

    r = call("/user/match", client.get_user_matches, ouid, MATCHTYPE, 0, 1) if ouid else None
    results.append(("/user/match", r))
    match_ids = r.json() if r is not None and r.status_code == 200 else []

    results.append(("/match-detail", call("/match-detail", client.get_match_detail, match_ids[0]) if match_ids else None))
    results.append(("/user/trade", call("/user/trade", client.get_user_trades, "buy", 0, 1)))
    results.append(("메타데이터 (matchtype)", call("meta", client.get_meta, "matchtype")))

    now = datetime.now(KST).strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        f"### 점검 확인 결과 ({now} KST)",
        "",
        "| API | 상태 코드 | 에러 코드 | 메시지 |",
        "|---|---|---|---|",
    ]
    for name, response in results:
        status, code, message = describe(response)
        lines.append(f"| {name} | {status} | {code} | {message} |")
    report = "\n".join(lines)

    print(report)
    summary_path = os.getenv("GITHUB_STEP_SUMMARY")
    if summary_path:
        with open(summary_path, "a", encoding="utf-8") as f:
            f.write(report + "\n")


if __name__ == "__main__":
    main()
