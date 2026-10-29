![API Test](https://github.com/owen970517/FConline_api_test/actions/workflows/api-test.yml/badge.svg)

# FC 온라인 Open API 테스트 자동화

NEXON Open API 중 **FC 온라인** API를 대상으로 한 API 테스트 자동화 프로젝트입니다.
테스트 케이스를 먼저 설계하고, 문서와 실제 동작을 직접 호출해 비교한 뒤 Python + pytest로 자동화했습니다.

- 테스트 대상: [NEXON Open API - FC 온라인](https://openapi.nexon.com/ko/game/fconline/)
- 테스트 케이스: 13개 (정상 3 / 경계값 4 / 예외 6)
- 결과: 13 passed

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
    └── test_apiError.py   # 테스트 케이스
    └── test_auth.py  
    └── test_match.py  
    └── test_metadata.py  
    └── test_user.py              
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

**테스트 데이터 전제 조건**: TC-04, TC-05는 테스트 계정이 공식 경기(`matchtype` = 50)를 **100경기 이상** 플레이한 기록이 있어야 통과합니다.
API는 기록이 요청 개수보다 적으면 있는 만큼만 반환하고, 기록이 없으면 200과 빈 배열(`[]`)을 반환합니다.
따라서 기록이 적은 계정에서는 API가 정상이어도 "정확히 100개"를 기대하는 TC-05가 실패합니다.
"100개 이하"로 검증하면 서버가 `limit`을 무시하고 더 적게 반환해도 통과하므로, `limit` 동작을 확실히 검증하기 위해 "정확히 100개"를 기대값으로 정했습니다.

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

**5. 수동 확인과 자동화 결과가 달랐던 사례**
Postman으로 "키 없음"을 확인했을 때는 OPENAPI00005가 나왔지만, 자동화 테스트(TC-12)는 OPENAPI00004로 실패했습니다.
실패한 테스트를 지우는 대신 `response.request.headers`로 실제 전송 헤더를 확인했고, 자동화 테스트는 키 헤더 없이 요청했음을 확인했습니다.
이후 Postman에서 키 헤더를 확실히 빼고 다시 요청한 결과 동일하게 OPENAPI00004가 반환되어, 처음의 수동 확인이 잘못되었음을 확인했습니다.
실제 동작(00004)을 기대값으로 정리했고, 수동 확인 결과도 실제 요청 내용을 검증한 뒤 기록하는 계기가 되었습니다.