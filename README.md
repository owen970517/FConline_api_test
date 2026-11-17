![API Test](https://github.com/owen970517/FConline_api_test/actions/workflows/api-test.yml/badge.svg)

# FC 온라인 Open API 테스트 자동화

NEXON Open API의 **FC 온라인** API를 테스트하는 프로젝트입니다.
테스트 케이스를 먼저 표로 정리하고, 문서 내용과 실제 응답을 직접 호출해 비교한 다음 Python + pytest로 자동화했습니다.

- 테스트 대상: [NEXON Open API - FC 온라인](https://openapi.nexon.com/ko/game/fconline/)
- 테스트 케이스: 34개 (정상 5 / 경계값 7 / 예외 11 / 교차 검증 4 / 규칙 검증 7)
- 결과: 34 passed / GitHub Actions에서 push할 때마다, 그리고 매일 자동 실행
    - 최근 경기 중 몰수 경기가 없으면 33 passed, 1 skipped

## 기술 스택

| 구분 | 사용 기술 |
|---|---|
| 언어 | Python 3 |
| 테스트 프레임워크 | pytest |
| HTTP 클라이언트 | requests |
| 환경 변수 관리 | python-dotenv |
| CI | GitHub Actions |

## 폴더 구조

```
fconline_api_test/
├── .github/
│   └── workflows/
│       └── api-test.yml   # GitHub Actions 워크플로
├── api_client.py          # API 호출을 모아둔 클라이언트 (FcOnlineClient)
├── conftest.py            # 공통 fixture (client, ouid)와 환경 변수 로드
├── pytest.ini             # pytest 설정
├── requirements.txt       # 의존 패키지
├── .env                   # API 키, 테스트 닉네임 (Git에 올리지 않음)
├── .gitignore
└── tests/
    ├── apiError.py           # 에러 응답 공통 검사 함수 (assert_api_error)
    ├── test_auth.py          # API 키
    ├── test_match.py         # 매치 기록 조회
    ├── test_match_detail.py  # 매치 상세 조회
    ├── test_metadata.py      # 메타데이터
    ├── test_trade.py         # 거래 기록 조회
    └── test_user.py          # 유저 정보, 최고 등급 조회
```

## 실행 방법

### 1. 설치

```bash
python -m venv venv
venv\Scripts\activate          # Mac/Linux: source venv/bin/activate
pip install -r requirements.txt
```

### 2. 환경 변수 설정

[NEXON Open API](https://openapi.nexon.com)에서 애플리케이션을 등록해 API 키를 발급받고,
프로젝트 루트에 `.env` 파일을 만듭니다.

```
NEXON_API_KEY=발급받은_API_키
TEST_NICKNAME=테스트에_사용할_닉네임
```

> `.env`는 `.gitignore`에 넣어 두어 저장소에 올라가지 않습니다.
> 키를 설정하지 않고 실행하면 테스트가 하나하나 API 오류로 실패하지 않고, `NEXON_API_KEY 환경변수가 설정되지 않았습니다` 메시지를 띄우고 바로 멈춥니다.

### 3. 실행

```bash
pytest -v                      # 전체 실행
pytest -v -k 경계값             # 이름으로 골라 실행
```

### 4. 자동 실행 (GitHub Actions)

`main` 브랜치에 push하거나 PR을 올리면 GitHub Actions에서 테스트가 자동으로 실행됩니다.
코드를 건드리지 않아도 API 동작은 바뀔 수 있어서, 매일 한국 시간 오전 9시 18분에도 한 번씩 실행합니다.

- 정각이 아니라 18분으로 정한 건, GitHub Actions 문서에 매시 정각에는 실행이 몰려 늦어지거나 빠질 수 있다고 나와 있기 때문입니다.
- 목요일은 게임 정기 점검이 있고 점검 시간도 매주 달라서 뺐습니다.
- cron은 기본적으로 UTC 기준이라 `timezone: "Asia/Seoul"`을 지정해 시각과 요일을 한국 시간으로 맞췄습니다.
- 같은 API 키의 호출 한도를 나눠 쓰기 때문에 `concurrency`로 테스트가 동시에 실행되지 않게 했고, API 응답이 멈추는 경우를 대비해 실행 시간을 10분으로 제한했습니다.

API 키와 테스트 닉네임은 GitHub Secrets(`NEXON_API_KEY`, `TEST_NICKNAME`)에 등록해 두었습니다.
코드는 그대로 두고 환경 변수만 바꿔서 로컬과 CI에서 같은 테스트를 실행합니다.

## 테스트 케이스

기대 결과는 모두 Postman과 테스트 코드로 실제 응답을 확인한 값입니다.

| ID | 구분 | API | 입력 | 기대 결과 |
|---|---|---|---|---|
| TC-01 | 정상 | /id | 존재하는 닉네임 | 200, `ouid`가 문자열로 존재 |
| TC-02 | 정상 | /user/basic | TC-01의 `ouid` | 200, `ouid`·`nickname`은 문자열, `level`은 1 이상의 정수, `ouid`와 `nickname`이 요청 값과 같음 |
| TC-03 | 정상 | 메타데이터 (매치 종류) | API 키 없이 요청 | 200, 목록이 비어 있지 않음, `matchtype`은 정수·`desc`는 문자열 |
| TC-04 | 경계값 | /user/match | `limit` = 1 | 200, 결과 1개 |
| TC-05 | 경계값 | /user/match | `limit` = 100 | 200, 결과 100개 |
| TC-06 | 경계값 | /user/match | `limit` = 0 | 400, OPENAPI00004, "Please input valid parameter" |
| TC-07 | 경계값 | /user/match | `limit` = 101 | 400, OPENAPI00004, "Please input valid parameter" |
| TC-08 | 예외 | /id | 존재하지 않는 닉네임 | 400, OPENAPI00004, "Please input valid parameter" |
| TC-09 | 예외 | /id | `nickname` 파라미터 없음 | 400, OPENAPI00004, "Please input valid parameter" |
| TC-10 | 예외 | /user/basic | 잘못된 `ouid` | 400, OPENAPI00003, "Please input valid id" |
| TC-11 | 예외 | /id | 잘못된 API 키 | 400, OPENAPI00005, "The apikey is not valid." |
| TC-12 | 예외 | /id | API 키 헤더 없음 | 400, OPENAPI00004, "Please input valid parameter" |
| TC-13 | 예외 | /id | API 키 빈 문자열 | 400, OPENAPI00004, "Please input valid parameter" |
| TC-14 | 교차 검증 | /user/maxdivision | 최고 등급 기록이 있는 계정의 `ouid` | 모든 항목의 `matchType`이 매치 종류 메타데이터(`matchtype`)에 존재 |
| TC-15 | 교차 검증 | /user/maxdivision | 최고 등급 기록이 있는 계정의 `ouid` | 모든 항목의 `division`이 등급 메타데이터(`divisionId`)에 존재 |
| TC-16 | 정상 | 메타데이터 (등급) | API 키 없이 요청 | 200, 목록이 비어 있지 않음, `divisionId`는 정수이고 중복 없음, `divisionName`은 문자열 |
| TC-17 | 규칙 검증 | /user/maxdivision | 최고 등급 기록이 있는 계정의 `ouid` | 모든 `achievementDate`가 날짜 형식이고, 현재 시각(한국 시간) 이후가 아님 |
| TC-18 | 교차 검증 | /user/trade | `tradetype` = buy, `limit` = 5 | 모든 거래의 `spid`가 선수 메타데이터(`id`)에 존재 |
| TC-19 | 규칙 검증 | /user/trade | `tradetype` = buy, `limit` = 100 | `tradeDate` 기준 최신 거래부터 내림차순 정렬 |
| TC-20 | 규칙 검증 | /user/trade | `tradetype` = sell, `limit` = 100 | `tradeDate` 기준 최신 거래부터 내림차순 정렬 |
| TC-21 | 경계값 | /user/trade | `tradetype` = buy, `limit` = 0 | 400, OPENAPI00004, "Please input valid parameter" |
| TC-22 | 경계값 | /user/trade | `tradetype` = buy, `limit` = 101 | 400, OPENAPI00004, "Please input valid parameter" |
| TC-23 | 경계값 | /user/trade | `tradetype` = buy, `offset` = -1 | 400, OPENAPI00004, "Please input valid parameter" |
| TC-24 | 예외 | /user/trade | 허용하지 않는 `tradetype` | 400, OPENAPI00004, "Please input valid parameter" |
| TC-25 | 예외 | /user/trade | `tradetype` 파라미터 없음 | 400, OPENAPI00004, "Please input valid parameter" |
| TC-26 | 정상 | /match-detail | 최근 공식 경기의 `matchid` | 200, `matchId`가 요청 값과 같음, `matchType`이 50, 참가자 2명 중 조회한 유저의 `ouid`가 있음 |
| TC-27 | 규칙 검증 | /match-detail | 최근 공식 경기 10개 | 모든 `matchDate`가 날짜 형식이고, 현재 시각(한국 시간) 이후가 아님 |
| TC-28 | 규칙 검증 | /match-detail | 최근 공식 경기 중 정상 종료(`matchEndType` = 0) 경기 | `matchResult`가 득점(`goalTotalDisplay`)과 일치. 득점이 같으면 승부차기(`shootOutScore`)로 승/패, 승부차기를 하지 않았으면 무 |
| TC-29 | 규칙 검증 | /match-detail | 최근 공식 경기 중 몰수 경기 | 한쪽이 몰수승(`matchEndType` = 1)·다른 쪽이 몰수패(2), 몰수승은 "승"·몰수패는 "패" |
| TC-30 | 규칙 검증 | /match-detail | 최근 공식 경기 중 정상 종료 경기 | 슈팅 상세(`shootDetail`) 개수가 `shootTotal`과 같고, 선수별 골 합계가 `goalTotal`과 같음 |
| TC-31 | 교차 검증 | /match-detail | 최근 공식 경기 10개 | `matchType`이 매치 종류 메타데이터에, 참가자의 `division`이 등급 메타데이터에 존재 |
| TC-32 | 예외 | /match-detail | 형식이 잘못된 `matchid` | 400, OPENAPI00004, "Please input valid parameter" |
| TC-33 | 예외 | /match-detail | 형식은 맞지만 존재하지 않는 `matchid` | 400, OPENAPI00004, "Please input valid parameter" |
| TC-34 | 예외 | /match-detail | `matchid` 파라미터 없음 | 400, OPENAPI00004, "Please input valid parameter" |

### 테스트 데이터 전제 조건

**매치 기록 (TC-04, TC-05)**
- 테스트 계정에 공식 경기(`matchtype` = 50) 기록이 100경기 이상 있어야 합니다.
- API는 기록이 요청한 개수보다 적으면 있는 만큼만 주고, 아예 없으면 200과 빈 배열(`[]`)을 줍니다. 그래서 기록이 적은 계정이면 API에 문제가 없어도 TC-05가 실패합니다.
- 기대값을 "100개 이하"로 두면 서버가 `limit`을 무시하고 더 적게 줘도 통과해 버립니다. `limit`이 제대로 동작하는지 확인하려고 "정확히 100개"로 정했습니다.

**최고 등급 (TC-14, TC-15, TC-17)**
- 테스트 계정에 최고 등급 기록이 1개 이상 있어야 합니다. 기록이 없으면 빈 목록이 와서 검증할 대상이 없기 때문에, 준비 단계(`max_divisions` fixture)에서 이유를 알려 주고 멈춥니다.
- 응답의 시각에는 시간대 표시가 없어서 TC-17은 이를 한국 시간(UTC+9)으로 보고 비교합니다. GitHub Actions 서버는 UTC로 동작하기 때문에, 현재 시각도 한국 시간으로 바꿔야 최근 기록이 미래 시각으로 잘못 판정되지 않습니다.

**거래 기록 (TC-18 ~ TC-25)**
- `TEST_NICKNAME` 계정이 아니라 API 키를 발급받은 계정의 거래 기록을 조회합니다.
- TC-18은 구매 기록이 1건 이상, TC-19·TC-20은 구매와 판매 기록이 각각 2건 이상 필요합니다. 부족하면 이유를 메시지로 보여 주고 실패합니다.

**매치 상세 (TC-26 ~ TC-31)**
- 최근 공식 경기 10개를 한 번만 조회해서 여러 테스트에서 같이 씁니다.
- TC-28, TC-30은 그중 정상 종료된 경기가 1개 이상 있어야 하고, 없으면 이유를 보여 주고 실패합니다.
- 몰수 경기는 진 쪽 기록이 `null`로 올 수 있어서 TC-28, TC-30에서는 빼고 TC-29에서 따로 확인합니다.
- 몰수 경기는 자주 나오지 않아서, 최근 10경기에 없으면 TC-29는 실패가 아니라 skip으로 처리됩니다.

## 설계 포인트

### 1. API 호출은 클라이언트에 모으기
테스트 코드에서는 URL을 직접 만들지 않고 `FcOnlineClient`의 메서드만 호출합니다.
엔드포인트 주소가 바뀌면 `api_client.py`만 고치면 됩니다.

### 2. API 키는 밖에서 넣어 주기
클라이언트가 환경 변수를 직접 읽지 않고, 생성할 때 키를 받습니다.
그래서 정상 테스트에는 진짜 키를, 예외 테스트에는 잘못된 키·빈 키·키 없음을 넣어서 같은 클라이언트를 그대로 씁니다.
키를 `None`으로 주면 헤더를 아예 보내지 않아서 "헤더 없음" 요청도 만들 수 있습니다.

### 3. fixture와 scope
- `client`, `ouid` fixture는 `scope="session"`이라 전체 테스트에서 한 번만 만들어집니다. 연결을 재사용하니 빠르고, 테스트끼리 바꾸는 상태가 없어서 같이 써도 문제가 없습니다.
- `ouid` fixture 안에서도 상태 코드를 확인해서, 준비 단계에서 실패하면 서버 응답이 메시지에 그대로 나옵니다.
- `ouid` fixture에서 이미 `/id`를 호출하지만 TC-01은 따로 두었습니다. `/id`가 고장 나면 결과에 "TC-01 FAILED"가 남아 어디가 문제인지 바로 보이고, 테스트 케이스 표와 실행 결과도 1:1로 맞출 수 있습니다.

### 4. 검증 방식
- 레벨처럼 계속 바뀌는 값은 고정값으로 비교하지 않고 "1 이상의 정수" 같은 규칙으로 확인합니다.
- 파이썬에서는 `isinstance(True, int)`가 `True`라서, 타입은 `type(값) is 타입`으로 검사합니다.
- 같은 400이라도 원인이 다를 수 있어서 상태 코드뿐 아니라 에러 코드(`name`)와 메시지까지 확인합니다. 이 검사는 `assert_api_error` 함수로 묶었습니다.
- 예외 테스트는 한 번에 하나만 틀리게 합니다. 예를 들어 API 키 예외 테스트는 존재하는 닉네임으로 요청해서, 실패 원인이 키 하나뿐이게 했습니다.
- 쿼리 파라미터는 `params=`로 넘깁니다. 닉네임에 `&`, `#` 같은 문자가 있어도 `requests`가 알아서 URL 인코딩해 줍니다.

## 관찰 기록

문서와 실제 응답을 비교하면서 알게 된 내용입니다.

**1. 잘못된 ouid와 없는 닉네임은 서로 다른 에러가 온다**
잘못된 `ouid`는 OPENAPI00003("valid id")을, 존재하지 않는 닉네임·파라미터 누락·범위 밖 `limit`은 OPENAPI00004("valid parameter")를 돌려줍니다.
없는 닉네임도 식별자 오류(00003)일 거라고 예상했는데, 서버는 닉네임을 식별자가 아니라 파라미터로 처리하고 있었습니다.

**2. OPENAPI00004만 봐서는 원인을 알 수 없다**
없는 닉네임(TC-08)과 닉네임 누락(TC-09)은 에러 코드와 메시지가 똑같아서 응답만으로는 구분이 안 됩니다.
그래서 같은 클라이언트 메서드를 쓰는 정상 케이스(TC-01)가 통과하는지로 파라미터 이름이 맞다는 걸 확인합니다.
원인별로 메시지가 다르게 나온다면 디버깅이 훨씬 쉬워질 것 같습니다.

**3. 범위 밖 limit은 보정되지 않고 거부된다**
`limit`이 0이나 101이면 최대값으로 맞춰 주지 않고 OPENAPI00004로 거부합니다.
`limit`을 빼고 요청하면 경기 기록이 최대 100개까지 옵니다.
경기 기록이 없을 때는 에러가 아니라 200과 빈 배열(`[]`)이 옵니다.

**4. API 키가 틀린 경우와 없는 경우를 다르게 처리한다**
잘못된 키는 OPENAPI00005, 헤더가 없거나 빈 문자열이면 OPENAPI00004가 옵니다.

**5. 몰수패 쪽 기록은 경기마다 다르게 온다**
몰수 경기(`matchEndType` 1·2)를 보다가 몰수패 쪽 기록이 경기마다 다르게 온다는 걸 발견했습니다. 최근 100경기에 있던 몰수 경기 3개를 비교해 보니, 2경기는 몰수패 쪽 슈팅·패스·점유율이 전부 `null`이고 선수 목록도 비어 있었는데, 나머지 1경기는 기록이 정상적으로 남아 있었습니다. 명세에는 몰수 경기의 기록이 어떻게 오는지 설명이 없습니다.
명세의 `goalTime` 규칙으로 이긴 쪽의 마지막 슈팅 시간을 계산해 봤더니, 기록이 남은 경기는 전반 22분, `null`인 경기는 후반 54분과 연장 전반 103분이었습니다. 몰수된 시점에 따라 기록 저장 여부가 달라지는 것 같지만, 표본이 3경기뿐이고 실제 몰수 시점은 응답에 없어서 확정하지는 못했습니다.
그래서 몰수 경기는 승패 규칙 검증(TC-28, TC-30)에서 빼고, 몰수 결과만 TC-29에서 따로 확인합니다.

## 트러블슈팅

### 연속으로 실행하면 429 에러로 테스트가 실패

**문제**
`pytest -v`로 전체 테스트를 연달아 실행했더니 25개 중 16개만 통과하고 6개는 실패, 3개는 에러가 났습니다. 실패 메시지는 전부 `assert 429 == 200`이었고, 에러 코드는 OPENAPI00007이었습니다. 에러 3개는 fixture가 준비 단계에서 429를 받아 테스트 자체가 실행되지 못한 경우였습니다.

**원인**
실행할 때마다 실패하는 테스트가 달라졌고, 하나씩 따로 돌리면 통과했습니다.
NEXON Open API 명세를 확인해 보니 OPENAPI00007(429)은 API 호출량 초과를 뜻했습니다.
간격 없이 연속으로 요청해 보니 6번째 요청에서 429가 왔고, 응답 헤더에 `x-ratelimit-limit: 5`가 있었습니다. [NEXON Open API 가이드](https://openapi.nexon.com/ko/guide/ai-agent/)에 나온 개발 단계 키의 호출 허용량(초당 최대 5건, 하루 최대 1,000건) 중 초당 한도와 같은 값입니다.
결국 서버 결함이 아니라, 테스트가 쉬지 않고 API를 호출하다가 키의 호출 한도를 넘은 것이었습니다.

**해결**
테스트마다 `sleep`을 넣으면 테스트를 추가할 때마다 같은 코드를 반복해야 합니다. 모든 요청이 `FcOnlineClient`를 거치기 때문에 클라이언트 한 곳에서 처리했습니다.
- 요청 사이에 최소 0.25초 간격을 둡니다.
- 429가 오면 1초, 2초, 4초씩 기다렸다가 최대 3번까지 다시 요청합니다.
- 기다리는 시간에는 0~1초의 무작위 시간(지터)을 더합니다. 같은 가이드에 고정 간격으로 재시도하면 요청이 같은 시점에 몰려 OPENAPI00007이 다시 날 수 있으니, 지수 백오프에 지터를 더하라고 나와 있어서 그대로 따랐습니다.
- 3번 다시 시도해도 429면 `RateLimitError`를 발생시켜 호출 한도 문제라는 걸 바로 알 수 있게 했습니다.
