# tests/tools/test_tools_deep.py
# 심층 조사 도구 E2E 테스트 — FHC-058 ~ FHC-064

import logging
import allure
from pages.tools.tools_deep_page import DeepPage
import pytest

logger = logging.getLogger(__name__)

pytestmark = [
    allure.epic("Tools"),
    allure.feature("심층 조사"),
    allure.story("심층 조사 해피패스"),
    pytest.mark.jira("KAN-7"),
    pytest.mark.skip(reason="서비스 업데이트로 Tools 기능 전체 종료됨"),
]


# ── fixtures ───────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def deep(login_module):
    """
    심층 조사 도구 fixture - 해피패스용 (모듈 공유)

    전제: login_module fixture로 로그인 완료 상태
    단계:
      1. login_module에서 (driver, wait) 수신 → DeepPage 생성
      2. 도구 목록 URL 직접 이동
      3. 심층 조사 도구 초기 세팅
    """
    tool = DeepPage(login_module)
    tool.navigate_to_tools()
    tool.setup_tool()
    return tool


@pytest.fixture
def deep_sad(login):
    """
    심층 조사 도구 fixture - 새드패스용 (독립 브라우저, FHC-062 전용)

    전제: login fixture로 로그인 완료 상태 (함수 스코프, 해피패스와 독립)
    단계:
      1. login에서 (driver, wait) 수신 → DeepPage 생성
      2. 도구 목록 URL 직접 이동
      3. 심층 조사 도구 초기 세팅
    """
    tool = DeepPage(login)
    tool.navigate_to_tools()
    tool.setup_tool()
    return tool


@pytest.fixture(scope="module")
def deep_sad_module(login_module):
    """
    심층 조사 도구 fixture - 경계값 새드패스용 (모듈 공유, FHC-063~064)

    전제: login_module fixture로 로그인 완료 상태
    단계:
      1. login_module에서 (driver, wait) 수신 → DeepPage 생성
      2. 도구 목록 URL 직접 이동
      3. 심층 조사 도구 초기 세팅
    """
    tool = DeepPage(login_module)
    tool.navigate_to_tools()
    tool.setup_tool()
    return tool


# ── 해피패스 ──────────────────────────────────────────────────────

@allure.story("심층 조사 해피패스")
@allure.title("[FHC-058] 심층 조사 메뉴 → 입력 → 생성 시작 확인 (Happy Path)")
@allure.severity(allure.severity_level.CRITICAL)
def test_deep_research_happy_path(deep):
    """
    [FHC-058~61] 심층 조사 해피패스 — 생성 시작까지

    전제: 로그인 완료 상태
    단계:
      1. LNB > '도구' 탭 클릭 → '심층 조사' 메뉴 클릭 (FHC-058)
      2. 주제 입력 필드에 '날씨' 입력 (FHC-059)
      3. 지시사항 입력 필드에 '대한민국 서울의 2026년 5월의 날씨' 입력 (FHC-060)
      4. [자동 생성] 버튼 클릭 → 로딩 스피너 확인 (FHC-061)
    기대: '심층 조사' 페이지 진입 → 버튼 활성화 → 생성 시작(스피너 표시)
    """
    logger.info("[FHC-058] 심층 조사 해피패스 시작")

    with allure.step("[FHC-058] 심층 조사 페이지 진입 확인"):
        deep.is_tool_page_displayed()

    with allure.step("[FHC-059~060] 주제 및 지시사항 입력"):
        deep.enter_text(DeepPage.TOPIC_INPUT, DeepPage.TOPIC_TEXT)
        deep.enter_text(DeepPage.MESSAGE_INPUT, DeepPage.MESSAGE_TEXT)

    with allure.step("[FHC-061] 생성 버튼 활성화 확인 및 클릭"):
        deep.assert_generate_btn_enabled()
        deep.click_generate()

    with allure.step("[FHC-061] 생성 시작(스피너) 확인"):
        assert deep.is_generating(), "생성이 시작되지 않았습니다"

    logger.info("[FHC-058~61] 심층 조사 해피패스 — 생성 시작 확인 완료")


@pytest.mark.slow
@allure.story("심층 조사 해피패스")
@allure.title("[FHC-061s] 심층 조사 생성 완료 확인 (slow)")
@allure.severity(allure.severity_level.CRITICAL)
def test_deep_research_is_generated(deep):
    """
    [FHC-058a] 심층 조사 생성 완료 확인 (최대 10분) — test_deep_research_happy_path 이후 실행

    전제: test_deep_research_happy_path에서 생성이 시작된 상태 (module fixture 공유)
    단계:
      1. 생성 완료 확인 (최대 10분) (FHC-061a)
    기대: 10분 이내 생성 완료
    """
    logger.info("[FHC-058a] 심층 조사 생성 완료 확인 시작")

    with allure.step("[FHC-061a] 생성 완료 확인 (최대 10분)"):
        assert deep.is_generated(timeout=600), "10분 이내 생성 실패"

    logger.info("[FHC-058a] 심층 조사 생성 완료 확인 완료")


# ── 새드패스 (해피패스와 독립) ───────────────────────────────────

@allure.story("주제 공백 입력 오류 메시지")
@allure.title("[FHC-062] 주제 공백 입력 시 오류 메시지 확인")
@allure.severity(allure.severity_level.NORMAL)
def test_blank_topic_error(deep_sad):
    """
    [FHC-062] 주제 공백 입력 시 오류 메시지 확인

    전제: 로그인 완료 상태 (독립 브라우저)
    단계:
      1. 주제 필드에 공백(' ') 입력
      2. 지시사항 필드 비움
      3. [자동 생성] 버튼 클릭
    기대: '답변 생성에 문제가 발생했습니다.' 오류 메시지 표시
    """
    logger.info("[FHC-062] 주제 공백 입력 시 오류 메시지 확인 시작")

    with allure.step("[FHC-062] 주제 공백 입력 후 생성 버튼 클릭"):
        deep_sad.enter_text(DeepPage.TOPIC_INPUT, DeepPage.TOPIC_BLANK)
        deep_sad.enter_text(DeepPage.MESSAGE_INPUT, "")
        deep_sad.click_generate()

    with allure.step("[FHC-062] 오류 메시지 표시 확인"):
        assert deep_sad.is_error_alert_displayed(), "오류 메시지가 표시되지 않았습니다"

    logger.info("[FHC-062] 주제 공백 입력 시 오류 메시지 확인 완료")


@allure.story("주제 500자 입력 버튼 활성화 경계값")
@allure.title("[FHC-063] 주제 500자 입력 → [자동 생성] 버튼 활성화 확인 (경계값)")
@allure.severity(allure.severity_level.NORMAL)
def test_topic_500_chars_btn_enabled(deep_sad_module):
    """
    [FHC-063] 주제 500자 입력 → [자동 생성] 버튼 활성화 확인 (경계값)

    전제: 로그인 완료 상태 (독립 브라우저)
    단계:
      1. 주제 필드에 500자 입력 ('가' * 500)
    기대:
      - 토큰 정상: [자동 생성] 버튼 활성화 (500자 허용 범위 내)
      - 토큰 소진: 버튼 비활성화 (xfail)
    """
    logger.info("[FHC-063] 주제 500자 입력 → 버튼 활성화 확인 시작")

    with allure.step("[FHC-063] 주제 500자 입력"):
        deep_sad_module.enter_text(DeepPage.TOPIC_INPUT, DeepPage.TOPIC_500_CHARS)

    with allure.step("[FHC-063] 생성 버튼 활성화 확인"):
        deep_sad_module.assert_generate_btn_enabled()

    logger.info("[FHC-063] 주제 500자 입력 → 버튼 활성화 확인 완료")


@allure.story("주제 501자 입력 버튼 비활성화 경계값")
@allure.title("[FHC-064] 주제 501자 입력 → [자동 생성] 버튼 비활성화 확인 (경계값)")
@allure.severity(allure.severity_level.NORMAL)
def test_topic_501_chars_btn_disabled(deep_sad_module):
    """
    [FHC-064] 주제 501자 입력 → [자동 생성] 버튼 비활성화 확인 (경계값)

    전제: 로그인 완료 상태 (독립 브라우저)
    단계:
      1. 주제 필드에 501자 입력 ('가' * 501)
    기대: [자동 생성] 버튼 비활성화 (501자 허용 범위 초과)
    """
    logger.info("[FHC-064] 주제 501자 입력 → 버튼 비활성화 확인 시작")

    with allure.step("[FHC-064] 주제 501자 입력"):
        deep_sad_module.enter_text(DeepPage.TOPIC_INPUT, DeepPage.TOPIC_501_CHARS)

    with allure.step("[FHC-064] 생성 버튼 비활성화 확인"):
        deep_sad_module.assert_generate_btn_disabled()

    logger.info("[FHC-064] 주제 501자 입력 → 버튼 비활성화 확인 완료")
