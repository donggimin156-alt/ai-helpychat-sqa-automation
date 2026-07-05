# tests/tools/test_tools_quiz.py
# 퀴즈 생성 도구 E2E 테스트 — FHC-055 ~ FHC-057

import logging
import allure
from pages.tools.tools_quiz_page import QuizPage
import pytest

logger = logging.getLogger(__name__)

pytestmark = [
    allure.epic("Tools"),
    allure.feature("퀴즈 생성"),
    allure.story("퀴즈 생성 해피패스"),
    pytest.mark.jira("KAN-9"),
    pytest.mark.skip(reason="서비스 업데이트로 퀴즈 생성 기능 삭제됨"),
]


# ── fixture ────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def quiz(login_module):
    """
    퀴즈 생성 도구 fixture (모듈 공유)

    전제: login_module fixture로 로그인 완료 상태
    단계:
      1. login_module에서 (driver, wait) 수신 → QuizPage 생성
      2. 도구 목록 URL 직접 이동
      3. 퀴즈 생성 도구 초기 세팅
    """
    tool = QuizPage(login_module)
    tool.navigate_to_tools()
    tool.setup_tool()
    return tool


# ── 해피패스 ──────────────────────────────────────────────────────


@allure.story("퀴즈 생성 해피패스")
@allure.title("[FHC-055] 퀴즈 생성 메뉴 → 입력 → 생성 → 완료 (Happy Path)")
@allure.severity(allure.severity_level.CRITICAL)
def test_quiz_happy_path(quiz):
    """
    [FHC-055~57] 퀴즈 생성 해피패스 (FHC-055 ~ FHC-057 통합)

    전제: 로그인 완료 상태
    단계:
      1. LNB > '도구' 탭 클릭 → '퀴즈 생성' 메뉴 클릭 (FHC-055)
      2. 문제 유형 '객관식 (단일 선택)', 난이도 '하', 주제 '퀴즈' 입력 (FHC-056)
      3. [자동 생성] 버튼 클릭 → 로딩 스피너 확인 → 생성 완료 (최대 2분) (FHC-057)
    기대: '퀴즈 생성' 페이지 진입 → 버튼 활성화 → 2분 이내 생성 완료
    """
    logger.info("[FHC-054] 퀴즈 생성 해피패스 시작")

    with allure.step("[FHC-055] 퀴즈 생성 페이지 진입 확인"):
        quiz.is_tool_page_displayed()

    with allure.step("[FHC-056] 문제 유형, 난이도, 주제 입력"):
        quiz.select_option(QuizPage.OPTION_TYPE_DD, QuizPage.OPTION_TYPE_VALUE)
        quiz.select_option(QuizPage.DIFFICULTY_DD, QuizPage.DIFFICULTY_VALUE)
        quiz.enter_text(QuizPage.CONTENT_INPUT, QuizPage.CONTENT_VALUE)

    with allure.step("[FHC-057] 생성 버튼 활성화 확인 및 클릭"):
        quiz.assert_generate_btn_enabled()
        quiz.click_generate()

    with allure.step("[FHC-057] 생성 시작(스피너) 확인"):
        assert quiz.is_generating(), "생성이 시작되지 않았습니다"

    with allure.step("[FHC-057] 생성 완료 확인 (최대 2분)"):
        assert quiz.is_generated(timeout=120), "2분 이내 퀴즈 생성 실패"
        
    logger.info("[FHC-055~57] 퀴즈 생성 해피패스 완료")
