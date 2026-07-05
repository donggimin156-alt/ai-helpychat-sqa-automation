# tests/tools/test_tools_lesson.py
# 수업지도안 도구 E2E 테스트 — FHC-045 ~ FHC-048

import os
import pytest
import logging
import allure
from pages.tools.tools_lesson_page import LessonPlanPage

logger = logging.getLogger(__name__)

pytestmark = [
    allure.epic("Tools"),
    allure.feature("수업지도안"),
    allure.story("수업지도안 생성 해피 케이스"),
]

COMMENT        = "없음"
REFERENCE_FILE = os.path.join(os.path.dirname(__file__), "../fixtures/file_choose_test.pdf")


# ── fixture ────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def page(login_module):
    driver, wait = login_module
    p = LessonPlanPage(driver, wait)
    p.navigate_to_tools()
    p.setup_tool()
    return p


# ── 테스트 케이스 ──────────────────────────────────────────────────

@allure.title("[FHC-045~048] 수업지도안 생성 해피 케이스")
@allure.severity(allure.severity_level.NORMAL)
def test_lesson_plan_happy_case(page):
    """
    [FHC-045~048] 수업지도안 생성 해피 케이스

    전제: 로그인 완료 상태
    단계:
      1. [FHC-045] '수업지도안' 메뉴 진입 확인
      2. [FHC-046] 필수 항목(학교급, 학년, 과목, 교육 내용, 수업 차시, 생성 방식) 선택 → [수업지도안 생성] 버튼 활성화 확인
      3. [FHC-047] 선택 항목(참고 자료, 기타 요청 사항) 입력 → [수업지도안 생성] 버튼 활성화 유지 확인
      4. [FHC-048] '다시 생성' 버튼 클릭 → 2분 이내 생성 완료 확인
    기대: 수업지도안 생성 정상 완료
    """
    with allure.step("[FHC-045] '수업지도안' 페이지 진입 확인"):
        logger.info("[FHC-045] 수업지도안 페이지 진입 확인")
        assert page.is_on_tool_page(), "수업지도안 도구 페이지 진입 실패"

    with allure.step("[FHC-046] 필수 항목 선택"):
        logger.info("[FHC-046] 필수 항목 입력 시작")
        if page.has_any_field_value():
            page.clear_all_fields()
        page.regen_with_random_values()
        assert page.is_generate_btn_enabled(), "필수 항목 선택 후 [수업지도안 생성] 버튼 비활성화"

    with allure.step("[FHC-047] 선택 항목 입력"):
        logger.info("[FHC-047] 선택 항목 입력 시작")
        page.scroll_to_upload_area()
        page.upload_reference(os.path.abspath(REFERENCE_FILE))
        page.enter_comment(COMMENT)
        assert page.is_generate_btn_enabled(), "선택 항목 입력 후 [수업지도안 생성] 버튼 비활성화"

    with allure.step("[FHC-048] '다시 생성' 버튼 클릭 및 생성 완료 확인"):
        logger.info("[FHC-048] 수업지도안 생성 시작")
        page.click_generate()
        assert page.is_generated(timeout=120), "2분 이내 수업지도안 생성 실패"

    logger.info("[FHC-045~048] 수업지도안 생성 해피 케이스 완료")
