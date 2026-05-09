# 스마트 일정 및 버스 통합 관리 시스템

개인 일정 관리와 청주시 버스 정보를 하나의 웹 서비스에서 사용할 수 있도록 만든 Flask 기반 프로젝트입니다. 사용자는 회원가입과 로그인을 통해 자신의 일정을 등록, 수정, 삭제할 수 있고, 버스 번호를 검색해 노선 정보와 정류장별 도착 정보를 확인할 수 있습니다. 관리자는 사용자, 일정, 접속 로그를 확인할 수 있습니다.

이 프로젝트는 일정 관리 기능과 공공데이터 버스 API를 결합해 사용자의 이동 계획을 더 효율적으로 관리하는 것을 목표로 합니다.

## 프로젝트 개요

일정 관리 앱은 보통 사용자의 계획만 보여주고, 버스 정보 앱은 교통 정보만 제공합니다. 이 프로젝트는 두 기능을 함께 제공하여 일정과 이동 정보를 한 화면에서 관리할 수 있도록 구성했습니다.

주요 구현은 `창업프로젝트/app.py`에 있으며, Flask 웹 서버, SQLite 데이터베이스, HTML 템플릿, 공공데이터 API 요청 로직이 포함되어 있습니다.

## 주요 기능

### 사용자 기능

- 회원가입
- 로그인 / 로그아웃
- 개인 일정 조회
- 일정 등록
- 일정 수정
- 일정 삭제
- 캘린더 화면에서 일정 확인

### 버스 정보 기능

- 청주시 버스 번호 검색
- 버스 노선 ID 조회
- 출발 정류장 / 도착 정류장 정보 조회
- 경유 정류장 목록 조회
- 정류장별 실시간 도착 예정 정보 조회
- 현재 버스가 가장 가까운 정류장 추정
- Folium 기반 버스 노선 지도 HTML 생성

### 관리자 기능

- 관리자 페이지 접근
- 전체 사용자 목록 조회
- 사용자별 일정 확인
- 전체 일정 조회
- 일정 삭제
- 로그인 / 로그아웃 등 사용자 활동 로그 조회

## 시스템 구성

```text
사용자 브라우저
  ↓
Flask 웹 서버
  ↓
라우팅 / 세션 / 템플릿 렌더링
  ↓
SQLite 데이터베이스
  ├─ users
  ├─ schedules
  └─ logs

Flask 웹 서버
  ↓
공공데이터포털 버스 API
  ├─ 버스 노선 조회
  ├─ 경유 정류장 조회
  └─ 정류장 도착 정보 조회
```

## 프로젝트 구조

```text
smart-schedule-bus-system/
│
├─ README.md
│
└─ 창업프로젝트/
   │
   ├─ Flask 앱
   │  ├─ app.py
   │  ├─ bussu.py
   │  ├─ schedule_module.py
   │  └─ mydb.py
   │
   ├─ 데이터베이스 / 데이터
   │  ├─ smartbus.db
   │  ├─ scheduler.db
   │  ├─ main.db
   │  ├─ New_Query_1758207725876.sql
   │  └─ 충청북도_청주시_버스정보시스템_20250401.csv
   │
   ├─ 템플릿
   │  ├─ templates/
   │  │  ├─ main.html
   │  │  ├─ login.html
   │  │  ├─ signup.html
   │  │  ├─ calendar.html
   │  │  ├─ bus.html
   │  │  ├─ bus_live.html
   │  │  ├─ admin.html
   │  │  ├─ admin_users.html
   │  │  ├─ admin_schedules.html
   │  │  └─ admin_logs.html
   │  │
   │  └─ static/
   │     └─ maps/
   │        └─ 생성된 버스 노선 지도 HTML
   │
   ├─ 지도 HTML
   │  ├─ cheongju_bus_map_311_....html
   │  ├─ cheongju_bus_map_407_....html
   │  ├─ cheongju_bus_map_502_....html
   │  └─ cheongju_bus_map_833_....html
   │
   └─ Java 클라이언트
      ├─ JavaFlaskClient.java
      ├─ pom.xml
      └─ lib/
         ├─ gson-2.10.1.jar
         ├─ json-20230227.jar
         └─ mysql-connector-j-9.4.0.jar
```

## 주요 파일 설명

| 파일 | 설명 |
| --- | --- |
| `창업프로젝트/app.py` | Flask 메인 서버 파일입니다. 로그인, 회원가입, 일정, 관리자, 버스 API 기능을 담당합니다. |
| `창업프로젝트/bussu.py` | 버스 번호, 노선 ID, 정류장 목록, 도착 정보를 조회하는 보조 모듈입니다. |
| `창업프로젝트/schedule_module.py` | 청주시 버스 노선 정보를 조회하고 Folium 지도 HTML을 생성하는 콘솔형 스크립트입니다. |
| `창업프로젝트/mydb.py` | 별도 SQLite DB 초기화 예제 모듈입니다. |
| `창업프로젝트/smartbus.db` | `app.py`에서 사용하는 SQLite 데이터베이스입니다. |
| `창업프로젝트/templates/` | Flask 화면을 구성하는 HTML 템플릿 폴더입니다. |
| `창업프로젝트/static/maps/` | 생성된 버스 지도 HTML 파일이 저장되는 폴더입니다. |
| `창업프로젝트/JavaFlaskClient.java` | Swing 기반 Java 클라이언트 예제입니다. 현재 Flask 라우트와 일부 API 경로가 다를 수 있습니다. |

## 기술 스택

- Python
- Flask
- SQLite
- HTML / Jinja2 Template
- Requests
- 공공데이터포털 버스 API
- XML / JSON 파싱
- Folium
- BeautifulSoup
- Java Swing

## 데이터베이스 구조

`app.py`는 실행 시 `smartbus.db`에 필요한 테이블을 자동으로 생성합니다.

### `users`

| 컬럼 | 설명 |
| --- | --- |
| `id` | 사용자 고유 ID |
| `username` | 로그인 아이디 |
| `password` | 비밀번호 |
| `name` | 사용자 이름 |
| `role` | `user` 또는 `admin` |

### `schedules`

| 컬럼 | 설명 |
| --- | --- |
| `id` | 일정 고유 ID |
| `user_id` | 일정을 등록한 사용자 ID |
| `title` | 일정 제목 |
| `date` | 일정 날짜 |
| `place` | 일정 장소 |

### `logs`

| 컬럼 | 설명 |
| --- | --- |
| `id` | 로그 고유 ID |
| `user_id` | 사용자 ID |
| `action` | 수행한 동작 |
| `detail` | 상세 내용 |
| `time` | 기록 시간 |

## 설치 방법

저장소를 클론합니다.

```bash
git clone https://github.com/kimayeong21/smart-schedule-bus-system.git
cd smart-schedule-bus-system/창업프로젝트
```

필요한 Python 패키지를 설치합니다.

```bash
pip install flask requests beautifulsoup4 folium
```

가상환경을 사용하는 경우 다음과 같이 설치할 수 있습니다.

```bash
python -m venv .venv
.venv\Scripts\activate
pip install flask requests beautifulsoup4 folium
```

## 실행 방법

Flask 서버를 실행합니다.

```bash
python app.py
```

실행 후 브라우저에서 다음 주소로 접속합니다.

```text
http://127.0.0.1:5000
```

## 화면 및 라우트 구성

| 경로 | 기능 |
| --- | --- |
| `/` | 메인 페이지 |
| `/login` | 로그인 |
| `/signup` | 회원가입 |
| `/logout` | 로그아웃 |
| `/calendar` | 사용자 일정 캘린더 |
| `/schedule` | 일정 추가, 수정, 삭제 처리 |
| `/bus` | 버스 검색 기본 화면 |
| `/bus/search` | 버스 번호로 노선 및 정류장 목록 조회 |
| `/bus/arrival` | 정류장 ID 기반 도착 정보 조회 |
| `/bus/where` | 특정 버스의 현재 위치 추정 |
| `/bus/live-ui` | 실시간 버스 UI 화면 |
| `/admin` | 관리자 메인 페이지 |
| `/admin/users` | 사용자 목록 |
| `/admin/user/<uid>` | 사용자 상세 및 일정 조회 |
| `/admin/schedules` | 전체 일정 관리 |
| `/admin/logs` | 사용자 활동 로그 |

## 사용 방법

### 일반 사용자

1. 메인 페이지에서 회원가입을 진행합니다.
2. 로그인 후 캘린더 화면으로 이동합니다.
3. 일정을 등록하거나 기존 일정을 수정, 삭제합니다.
4. 버스 메뉴에서 버스 번호를 검색해 노선과 정류장 정보를 확인합니다.

### 관리자

1. 회원가입 시 관리자 옵션을 선택합니다.
2. 관리자 ID는 대문자와 숫자 조합이어야 합니다.
3. 관리자 계정으로 로그인하면 관리자 페이지로 이동합니다.
4. 사용자 목록, 사용자별 일정, 전체 일정, 활동 로그를 확인합니다.

## 버스 API 기능

이 프로젝트는 공공데이터포털의 버스 정보 API를 사용합니다.

사용 중인 기본 설정은 다음과 같습니다.

```python
CITY_CODE = "33010"  # 청주시
```

주요 조회 흐름은 다음과 같습니다.

```text
버스 번호 입력
  ↓
routeId 조회
  ↓
노선 기본 정보 조회
  ↓
경유 정류장 목록 조회
  ↓
정류장 nodeId 선택
  ↓
실시간 도착 예정 정보 조회
```

## 지도 생성 기능

`schedule_module.py`를 실행하면 버스 번호를 입력받아 해당 노선의 정류장 좌표를 조회하고, Folium을 사용해 지도 HTML 파일을 생성합니다.

```bash
python schedule_module.py
```

생성되는 파일 이름은 다음과 같은 형식입니다.

```text
cheongju_bus_map_버스번호_고유ID.html
```

## 현재 구현상의 특징

- Flask 세션을 사용해 로그인 상태를 관리합니다.
- SQLite 기반으로 사용자, 일정, 로그 데이터를 저장합니다.
- `app.py` 실행 시 필요한 테이블이 자동 생성됩니다.
- 버스 API 응답은 JSON을 우선 사용하고 실패 시 XML 파싱을 시도합니다.
- 관리자 계정은 회원가입 시 관리자 옵션을 선택해 만들 수 있습니다.
- 일부 보조 파일은 실험 또는 확장용으로 포함되어 있습니다.

## 주의 사항

- 현재 공공데이터 API 서비스 키가 코드에 직접 포함되어 있습니다. 실제 배포 시에는 환경 변수로 분리하는 것이 좋습니다.
- 비밀번호는 암호화되지 않은 상태로 SQLite에 저장됩니다.
- Java 클라이언트는 `/api/...` 경로를 호출하도록 작성되어 있지만, 현재 Flask 메인 서버의 라우트와 일부 맞지 않을 수 있습니다.
- `pom.xml`은 dependency 태그 구조가 깨져 있어 Maven 빌드 전에 수정이 필요할 수 있습니다.
- 저장소에는 생성된 지도 HTML, DB 파일, 캐시 파일이 함께 포함되어 있습니다.
- 실시간 버스 정보는 공공데이터 API 응답 상태와 네트워크 상황에 따라 달라질 수 있습니다.

## 개선 아이디어

- API 키를 `.env` 또는 환경 변수로 분리
- 비밀번호 해시 처리 적용
- Java 클라이언트와 Flask API 라우트 정합성 맞추기
- `requirements.txt` 추가
- DB 파일과 캐시 파일을 `.gitignore`로 관리
- 지도 생성 파일 저장 위치 통일
- 일정과 버스 도착 시간을 연결한 출발 알림 기능 추가
- 일정 장소 기준 가까운 정류장 추천 기능 추가
- 관리자 권한 관리 강화
- UI 디자인 개선 및 모바일 대응

## 활용 분야

- Flask 웹 프로젝트 실습
- SQLite 데이터베이스 연동 학습
- 공공데이터 API 활용 프로젝트
- 버스 정보 서비스 프로토타입
- 일정 관리 시스템 구현
- 캡스톤 디자인 및 창업 프로젝트 발표

## 개발자

김아영
