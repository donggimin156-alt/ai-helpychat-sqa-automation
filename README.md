# AI Helpy Chat UI QA 자동화 프로젝트

엘리스 기업용 생성형 AI 플랫폼 **AI Helpy Chat**의 웹 UI를 대상으로 E2E 테스트 자동화를 진행한 프로젝트입니다.

기간: 2026.05.13 ~ 2026.06.01

팀: 4인

* * *

브랜치 구성

selenium  Python + Selenium + Pytest 기반 팀 프로젝트

* * *

사용 도구

Python, Pytest, Selenium WebDriver, pytest-xdist, Allure Report, GitLab CI/CD, Discord Webhook, Jira

브라우저를 직접 구동해 사용자 시나리오를 그대로 재현하는 방식으로 검증합니다. 자동화 67건(기능 61건 + 부하 6건)을 작성했고, GitLab CI에서 `main`·`develop` push 시 파이프라인이 돌아 테스트 실행 → Allure 리포트 생성 → GitLab Pages 배포 → Discord 알림까지 이어집니다. CI는 `slow`와 `xfail` 마커를 제외해 59건을 상시 회귀로 실행합니다.

알려진 제품 결함은 `xfail`, 서비스가 종료된 기능은 `skip`으로 구분해 표시합니다. 실패를 숨기지 않으면서 CI가 항상 빨간 상태로 남지 않게 하려는 의도이며, 결함이 수정되면 XPASS로 드러납니다.

* * *

디렉터리 구조

    tests/            도메인별 시나리오 · 검증
                      login, chat, mypage, settings, tools, token,
                      agent, logout, signup
    pages/
      base_page.py    공통 동작 · 대기 처리 (BasePage)
      tools/          기능별 Base + 세부 Page (base_tool_page 등)
      ...             도메인별 Page Object
    config/
      settings.py         URL · 계정 · 대기시간 상수 (SSOT)
      login_helpers.py    로그인 · 쿠키 캐싱
      browser_factory.py  브라우저 생성 옵션
    conftest.py       공용 fixture (driver, wait, login, module scope 등)
    plugins/          Pytest 플러그인 (Allure, 로깅, 리포팅·Jira 연동)
    performance/      부하 테스트 6건
    utils/            Jira 연동 · 랜덤 데이터 생성
    scripts/          테스트 계정 재생성 스크립트
    docs/             테스트 결과 집계 데이터
    .gitlab-ci.yml    CI 파이프라인 정의

* * *

내가 한 것:

Page Object Model 계층 구조를 설계하고, 마이페이지 · 설정 · 도구 도메인의 테스트 케이스 작성을 담당했습니다.

**계층 구조 설계.** 테스트 코드에 흩어져 있던 로케이터와 UI 조작을 Page 계층으로 옮겼습니다. `BasePage`가 클릭 · 입력 · 대기 같은 공통 동작을 담당하고, `tools`처럼 화면이 많은 도메인은 기능별 Base(`base_tool_page`)를 한 겹 더 두어 중복을 줄였습니다. 현재 로케이터 188개가 전부 Page 계층에 있고 테스트 코드에는 원시 로케이터가 하나도 남아 있지 않습니다. UI가 바뀌어도 테스트를 고치지 않고 Page 파일만 수정하면 됩니다.

**Fixture scope 최적화.** 로그인이 필요한 테스트마다 브라우저를 새로 띄우고 로그인을 반복하던 구조를, 모듈 단위로 브라우저와 세션을 공유하도록 바꿨습니다. Setup 실행이 58회에서 24회로 줄어 누적 시간이 551초에서 228초로 **58.6% 단축**됐습니다(회당 약 9.5초). 테스트 간 독립성이 필요한 경우를 위해 function scope fixture도 함께 유지합니다.

**리포팅 · 알림.** 실패 시 스크린샷 · DOM · 콘솔 로그가 Allure 리포트에 자동으로 첨부되도록 플러그인을 구성했고, 실행 결과 요약이 Discord로 전송됩니다. Jira 마커를 붙인 테스트는 실패 시 해당 이슈에 자동으로 코멘트가 달립니다.

자동화 67건 (기능 61건 + 부하 6건) · CI 상시 회귀 59건

* * *

실행 방법

    python -m venv venv
    source venv/Scripts/activate
    pip install -r config/requirements.txt

`.env.example`을 `.env`로 복사해 계정 정보를 채웁니다. `.env`는 gitignore 대상입니다.

    # 기본 실행 (slow 마커 제외)
    pytest

    # 특정 도메인만 실행
    pytest tests/mypage/
    pytest tests/tools/

    # slow 마커까지 전체 실행
    pytest -m ""

    # 병렬 실행 — 코어 수에 맞춰 지정
    # (-n auto는 논리 프로세서 수만큼 브라우저가 떠서 세션 충돌이 발생할 수 있음)
    pytest -n 4 --dist=loadfile

    # Allure 리포트를 브라우저로 열기
    pytest tests/폴더명/ --open

    # Discord 알림 전송
    pytest tests/폴더명/ --discord

    # Jira 이슈 연동 활성화
    pytest --jira

* * *

Allure 설치 (Windows)

Allure 리포트를 로컬에서 열려면 CLI가 필요합니다. Scoop으로 Java와 Allure를 설치합니다.

    # Scoop이 없다면 먼저 설치 (PowerShell)
    Set-ExecutionPolicy RemoteSigned -Scope CurrentUser
    irm get.scoop.sh | iex

    # Java (Allure 실행에 필요)
    scoop bucket add java
    scoop install temurin-lts

    # Allure CLI + Python 패키지
    scoop install allure
    pip install allure-pytest

    # 설치 확인
    java -version
    allure --version
