![API Test](https://github.com/owen970517/FConline_api_test/actions/workflows/api-test.yml/badge.svg)

# FC 온라인 Open API 테스트 자동화

NEXON Open API 중 **FC 온라인** API를 대상으로 한 API 테스트 자동화 프로젝트입니다.
테스트 케이스를 먼저 설계하고, 문서와 실제 동작을 직접 호출해 비교한 뒤 Python + pytest로 자동화했습니다.

- 테스트 대상: [NEXON Open API - FC 온라인](https://openapi.nexon.com/ko/game/fconline/)
- 테스트 케이스: 34개 (정상 5 / 경계값 7 / 예외 11 / 교차 검증 4 / 규칙 검증 7)
- 결과: 34 passed / GitHub Actions에서 push마다 자동 실행
    - 최근 전적 중 "몰수 경기"가 존재하지 않을 경우 33 passed, 1 skipped

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

[NEXON Open API](https://openapi.nexon.com)에서 애플리케이션을 등록해 API 키를 발급받은 뒤,
프로젝트 루트에 `.env` 파일을 만듭니다.

```
NEXON_API_KEY=발급받은_API_키
TEST_NICKNAME=테스트에_사용할_닉네임
```

> `.env`는 `.gitignore`에 포함되어 있어 저장소에 올라가지 않습니다.
> 키가 설정되지 않으면 모든 테스트가 API 오류로 실패하는 대신, `NEXON_API_KEY 환경변수가 설정되지 않았습니다` 메시지로 바로 중단됩니다.

### 3. 실행

```bash
pytest -v                      # 전체 실행
pytest -v -k 경계값             # 이름으로 골라 실행
```

### 4. 자동 실행 (GitHub Actions)

`main` 브랜치에 push하거나 PR을 열면 GitHub Actions에서 테스트가 자동으로 실행됩니다.
API 키와 테스트 닉네임은 저장소의 GitHub Secrets(`NEXON_API_KEY`, `TEST_NICKNAME`)에 등록해 사용하며,
코드는 수정하지 않고 실행 환경만 바뀌어도 같은 테스트가 동작합니다.

## 테스트 케이스

근거가 "직접 확인"인 항목은 Postman과 자동화 테스트로 실제 응답을 확인한 값입니다.

| ID | 구분 | API | 입력 | 기대 결과 | 근거 |
|---|---|---|---|---|---|
| TC-01 | 정상 | /id | 존재하는 닉네임 | 200, `ouid`가 문자열로 존재 | 직접 확인 |
| TC-02 | 정상 | /user/basic | TC-01의 `ouid` | 200, `ouid`·`nickname`은 문자열, `level`은 1 이상의 정수, `ouid`와 `nickname`이 요청 값과 같음 | 직접 확인 |
| TC-03 | 정상 | 메타데이터 (매치 종류) | API 키 없이 요청 | 200, 목록이 비어 있지 않음, `matchtype`은 정수·`desc`는 문자열 | 직접 확인 |
| TC-04 | 경계값 | /user/match | `limit` = 1 | 200, 결과 1개 | 직접 확인 |
| TC-05 | 경계값 | /user/match | `limit` = 100 | 200, 결과 100개 | 직접 확인 |
| TC-06 | 경계값 | /user/match | `limit` = 0 | 400, OPENAPI00004, "Please input valid parameter" | 직접 확인 |
| TC-07 | 경계값 | /user/match | `limit` = 101 | 400, OPENAPI00004, "Please input valid parameter" | 직접 확인 |
| TC-08 | 예외 | /id | 존재하지 않는 닉네임 | 400, OPENAPI00004, "Please input valid parameter" | 직접 확인 |
| TC-09 | 예외 | /id | `nickname` 파라미터 없음 | 400, OPENAPI00004, "Please input valid parameter" | 직접 확인 |
| TC-10 | 예외 | /user/basic | 잘못된 `ouid` | 400, OPENAPI00003, "Please input valid id" | 직접 확인 |
| TC-11 | 예외 | /id | 잘못된 API 키 | 400, OPENAPI00005, "The apikey is not valid." | 직접 확인 |
| TC-12 | 예외 | /id | API 키 헤더 없음 | 400, OPENAPI00004, "Please input valid parameter" | 직접 확인 |
| TC-13 | 예외 | /id | API 키 빈 문자열 | 400, OPENAPI00004, "Please input valid parameter" | 직접 확인 |
| TC-14 | 교차 검증 | /user/maxdivision | 최고 등급 기록이 있는 계정의 `ouid` | 모든 항목의 `matchType`이 매치 종류 메타데이터(`matchtype`)에 존재 | 직접 확인 |
| TC-15 | 교차 검증 | /user/maxdivision | 최고 등급 기록이 있는 계정의 `ouid` | 모든 항목의 `division`이 등급 메타데이터(`divisionId`)에 존재 | 직접 확인 |
| TC-16 | 정상 | 메타데이터 (등급) | API 키 없이 요청 | 200, 목록이 비어 있지 않음, `divisionId`는 정수이고 중복 없음, `divisionName`은 문자열 | 직접 확인 |
| TC-17 | 규칙 검증 | /user/maxdivision | 최고 등급 기록이 있는 계정의 `ouid` | 모든 `achievementDate`가 날짜 형식이고, 현재 시각(한국 시간) 이후가 아님 | 직접 확인 |
| TC-18 | 교차 검증 | /user/trade | `tradetype` = buy, `limit` = 5 | 모든 거래의 `spid`가 선수 메타데이터(`id`)에 존재 | 직접 확인 |
| TC-19 | 규칙 검증 | /user/trade | `tradetype` = buy, `limit` = 100 | `tradeDate` 기준 최신 거래부터 내림차순 정렬 | 문서, 직접 확인 |
| TC-20 | 규칙 검증 | /user/trade | `tradetype` = sell, `limit` = 100 | `tradeDate` 기준 최신 거래부터 내림차순 정렬 | 문서, 직접 확인 |
| TC-21 | 경계값 | /user/trade | `tradetype` = buy, `limit` = 0 | 400, OPENAPI00004, "Please input valid parameter" | 직접 확인 |
| TC-22 | 경계값 | /user/trade | `tradetype` = buy, `limit` = 101 | 400, OPENAPI00004, "Please input valid parameter" | 직접 확인 |
| TC-23 | 경계값 | /user/trade | `tradetype` = buy, `offset` = -1 | 400, OPENAPI00004, "Please input valid parameter" | 직접 확인 |
| TC-24 | 예외 | /user/trade | 허용하지 않는 `tradetype` | 400, OPENAPI00004, "Please input valid parameter" | 직접 확인 |
| TC-25 | 예외 | /user/trade | `tradetype` 파라미터 없음 | 400, OPENAPI00004, "Please input valid parameter" | 직접 확인 |
| TC-26 | 정상 | /match-detail | 최근 공식 경기의 `matchid` | 200, `matchId`가 요청 값과 같음, `matchType`이 50, 참가자 2명 중 조회한 유저의 `ouid`가 있음 | 직접 확인 |
| TC-27 | 규칙 검증 | /match-detail | 최근 공식 경기 10개 | 모든 `matchDate`가 날짜 형식이고, 현재 시각(한국 시간) 이후가 아님 | 직접 확인 |
| TC-28 | 규칙 검증 | /match-detail | 최근 공식 경기 중 정상 종료(`matchEndType` = 0) 경기 | `matchResult`가 득점(`goalTotalDisplay`)과 일치. 득점이 같으면 승부차기(`shootOutScore`)로 승/패, 승부차기를 하지 않았으면 무 | 직접 확인 |
| TC-29 | 규칙 검증 | /match-detail | 최근 공식 경기 중 몰수 경기 | 한쪽이 몰수승(`matchEndType` = 1)·다른 쪽이 몰수패(2), 몰수승은 "승"·몰수패는 "패" | 문서, 직접 확인 |
| TC-30 | 규칙 검증 | /match-detail | 최근 공식 경기 중 정상 종료 경기 | 슈팅 상세(`shootDetail`) 개수가 `shootTotal`과 같고, 선수별 골 합계가 `goalTotal`과 같음 | 직접 확인 |
| TC-31 | 교차 검증 | /match-detail | 최근 공식 경기 10개 | `matchType`이 매치 종류 메타데이터에, 참가자의 `division`이 등급 메타데이터에 존재 | 직접 확인 |
| TC-32 | 예외 | /match-detail | 형식이 잘못된 `matchid` | 400, OPENAPI00004, "Please input valid parameter" | 직접 확인 |
| TC-33 | 예외 | /match-detail | 형식은 맞지만 존재하지 않는 `matchid` | 400, OPENAPI00004, "Please input valid parameter" | 직접 확인 |
| TC-34 | 예외 | /match-detail | `matchid` 파라미터 없음 | 400, OPENAPI00004, "Please input valid parameter" | 직접 확인 |

### 테스트 데이터 전제 조건

**매치 기록 (TC-04, TC-05)**
- 테스트 계정이 공식 경기(`matchtype` = 50)를 **100경기 이상** 플레이한 기록이 있어야 통과합니다.
- API는 기록이 요청 개수보다 적으면 있는 만큼만 반환하고, 기록이 없으면 200과 빈 배열(`[]`)을 반환합니다. 따라서 기록이 적은 계정에서는 API가 정상이어도 "정확히 100개"를 기대하는 TC-05가 실패합니다.
- "100개 이하"로 검증하면 서버가 `limit`을 무시하고 더 적게 반환해도 통과하므로, `limit` 동작을 확실히 검증하기 위해 "정확히 100개"를 기대값으로 정했습니다.

**최고 등급 (TC-14, TC-15, TC-17)**
- 테스트 계정에 최고 등급 기록이 하나 이상 있어야 합니다. 기록이 없으면 빈 목록이 반환되어 검증할 대상이 없으므로, 이 경우 준비 단계(`max_divisions` fixture)에서 원인을 알려 주며 중단되도록 했습니다.
- TC-17은 응답의 시각에 시간대 표시가 없어 **한국 시간(UTC+9)으로 간주**하고 비교합니다. GitHub Actions 서버는 UTC로 동작하므로, 현재 시각도 한국 시간으로 맞춰 최근 기록이 미래로 잘못 판정되지 않도록 했습니다.

**거래 기록 (TC-18 ~ TC-25)**
- `TEST_NICKNAME` 계정이 아니라 **API 키를 발급받은 계정**의 기록을 조회합니다.
- TC-18은 구매 기록 1건 이상, TC-19·TC-20은 구매·판매 기록이 각각 2건 이상 있어야 하며, 부족하면 원인을 알려 주며 실패합니다.

**매치 상세 (TC-26 ~ TC-31)**
- 테스트 계정의 최근 공식 경기 10개를 한 번만 조회해 함께 사용합니다.
- TC-28, TC-30은 그중 정상 종료된 경기가 1개 이상 있어야 하며, 없으면 원인을 알려 주며 실패합니다.
- 몰수 경기는 진 쪽 기록이 비어 있을(`null`) 수 있어 TC-28, TC-30에서 제외하고 TC-29에서 따로 검증합니다.
- 몰수 경기는 드물게 발생하므로, 최근 10경기 안에 없으면 TC-29는 실패가 아닌 건너뜀(skip)으로 처리됩니다.

## 설계 포인트

### 1. API 호출 로직 분리
테스트 코드는 URL을 직접 다루지 않고 `FcOnlineClient`의 메서드만 호출합니다.
엔드포인트가 바뀌어도 `api_client.py`만 수정하면 됩니다.

### 2. API 키를 외부에서 주입
클라이언트가 환경 변수를 직접 읽지 않고, 생성할 때 키를 넘겨받습니다.
덕분에 정상 테스트는 진짜 키로, 예외 테스트는 잘못된 키·빈 키·키 없음으로 같은 클라이언트를 재사용할 수 있습니다.
키가 `None`이면 헤더 자체를 넣지 않아 "헤더 없음" 요청을 정확히 재현합니다.

### 3. fixture와 scope
- `client`, `ouid` fixture를 `scope="session"`으로 두어 테스트 전체에서 한 번만 생성합니다. 연결을 재사용해 빠르고, 테스트끼리 영향을 줄 상태가 없어 안전합니다.
- `ouid` fixture 안에서도 응답 코드를 검증해, 준비 단계가 실패하면 원인(서버 응답)이 메시지에 바로 표시되도록 했습니다.
- `ouid` fixture가 이미 `/id`를 호출하지만 TC-01을 별도 테스트로 두었습니다. `/id`가 고장 났을 때 결과에 "TC-01 FAILED"가 남아 원인이 바로 보이고, 테스트 케이스 표와 실행 결과가 1:1로 대응합니다.

### 4. 검증 방식
- **값이 바뀌는 데이터는 규칙으로 검증**: 레벨처럼 계속 바뀌는 값은 고정값 대신 "1 이상의 정수"로 확인합니다.
- **정확한 타입 검사**: 파이썬에서 `isinstance(True, int)`가 `True`이기 때문에 `type(값) is 타입`으로 검사합니다.
- **상태 코드만으로 판단하지 않음**: 같은 400이라도 원인이 다르므로 에러 코드(`name`)와 메시지까지 검증합니다. 공통 검사는 `assert_api_error` 함수로 묶었습니다.
- **한 번에 하나만 틀리게**: API 키 예외 테스트는 존재하는 닉네임으로 요청해, 실패 원인이 키뿐이도록 했습니다.
- **쿼리 파라미터는 `params=`로 전달**: 닉네임에 `&`, `#` 같은 문자가 있어도 `requests`가 자동으로 URL 인코딩합니다.

## 관찰 기록

문서와 실제 동작을 비교하며 확인한 내용입니다.

**1. 식별자 오류와 파라미터 오류를 구분한다**
잘못된 `ouid`는 OPENAPI00003("valid id"), 존재하지 않는 닉네임·파라미터 누락·범위 밖 `limit`은 OPENAPI00004("valid parameter")를 반환합니다.
처음에는 "존재하지 않는 닉네임"이 식별자 오류(00003)일 것으로 예상했지만, 서버는 닉네임을 식별자가 아닌 파라미터로 처리했습니다.

**2. OPENAPI00004는 원인을 구분할 수 없다**
존재하지 않는 닉네임(TC-08)과 닉네임 누락(TC-09)은 에러 코드와 메시지가 모두 같아, 응답만으로는 원인을 알 수 없습니다.
이를 보완하기 위해 같은 클라이언트 메서드를 쓰는 정상 케이스(TC-01)가 통과하는지로 파라미터 이름이 올바르다는 것을 보증합니다.
개선 제안: 원인별로 메시지를 다르게 제공하면 디버깅이 쉬워집니다.

**3. 범위 밖 `limit`은 보정되지 않고 거부된다**
`limit` = 0, 101은 최대값으로 조용히 맞춰지지 않고 OPENAPI00004로 거부됩니다.
`limit`을 생략하면 경기 기록이 최대 100개까지 반환됩니다.
경기 기록이 없는 경우에는 에러가 아닌 200과 빈 배열(`[]`)을 반환합니다.

**4. API 키가 "틀림"과 "없음"을 다르게 처리한다**
잘못된 키는 OPENAPI00005, 헤더가 없거나 값이 빈 문자열이면 OPENAPI00004를 반환합니다.

**5. 몰수패 쪽 기록은 경기마다 다르게 내려온다**
몰수 경기(`matchEndType` 1·2)를 확인하던 중, 몰수패 쪽 기록이 경기마다 다르게 내려오는 것을 발견했습니다. 최근 100경기 중 몰수 경기 3개를 비교한 결과, 2경기는 몰수패 쪽 슈팅·패스·점유율이 모두 `null`이고 선수 목록도 비어 있었지만, 1경기는 정상적으로 기록이 남아 있었습니다. 명세에는 몰수 시 기록이 어떻게 내려오는지 설명이 없습니다.
명세의 `goalTime` 규칙으로 이긴 쪽의 마지막 슈팅 시간을 계산해 보니, 기록이 남은 경기는 전반 22분이었고 `null`인 경기는 후반 54분, 연장 전반 103분이었습니다. 몰수된 시점에 따라 기록 저장 여부가 달라지는 것으로 보이지만, 표본이 3경기뿐이고 실제 몰수 시점은 응답에 없어 확정하지는 못했습니다.
이 때문에 몰수 경기는 승패 규칙 검증 테스트(TC-28, TC-30)에서 제외하고, 몰수 결과만 따로 검증(TC-29)합니다.

## 트러블슈팅

### 연속 실행 시 호출량 초과(429)로 테스트가 실패

**문제**
연속으로 `pytest -v`로 전체를 실행하면 25개 중 16개만 통과하고 6개는 실패, 3개는 에러가 났습니다. 실패 메시지는 모두 `assert 429 == 200`이었고, 에러 코드는 OPENAPI00007이었습니다. 에러 3개는 fixture가 준비 단계에서 429를 받아 테스트가 실행되지 못한 경우였습니다.

**원인 분석**
- 실행할 때마다 실패하는 테스트가 바뀌었고, 하나씩 따로 실행하면 통과했습니다.
- NEXON Open API 명세에서 OPENAPI00007(429)이 API 호출량 초과를 뜻한다는 것을 확인했습니다.
- 실제로 간격 없이 연속 요청하면 6번째 요청에서 429가 발생하며 응답 헤더에 `x-ratelimit-limit: 5`가 있었습니다. 이는 [NEXON Open API 가이드](https://openapi.nexon.com/ko/guide/ai-agent/)에 명시된 개발 단계 키의 호출 허용량(초당 최대 5건, 1일 최대 1,000건) 중 초당 한도와 일치합니다.

이를 근거로 테스트가 쉬지 않고 API를 호출하면서 키의 호출 한도를 넘은 것으로 보고, 서버 결함이 아닌 실행 환경 문제로 판단했습니다.

**해결**
테스트마다 `sleep`을 넣으면 테스트가 늘어날 때마다 같은 코드를 반복해야 합니다. 모든 요청은 `FcOnlineClient`를 거치므로 클라이언트 한 곳에서 처리했습니다.
- 요청 사이에는 최소 0.25초 간격을 둡니다.
- 429가 오면 1초, 2초, 4초로 늘려 가며 기다렸다가 최대 3번까지 다시 요청합니다.
- 이때 대기 시간에 0~1초의 무작위 시간(지터)을 더합니다. 같은 가이드에서 고정 간격으로 재시도하면 여러 요청이 같은 시점에 몰려 OPENAPI00007이 다시 발생하므로, 지수 백오프에 지터를 더해 재시도 시점을 흩뜨리도록 안내하고 있기 때문입니다.
- 그래도 429면 `RateLimitError`를 발생시켜 호출 한도 문제라는 걸 바로 알 수 있게 했습니다.
