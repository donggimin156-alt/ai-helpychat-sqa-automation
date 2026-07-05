# tests/tools/test_tools_ppt.py
# PPT 생성 도구 E2E 테스트 — FHC-049 ~ FHC-054

import pytest
import logging
import allure
from pages.tools.tools_ppt_page import PPTPage
from config.settings import DOWNLOAD_DIR

logger = logging.getLogger(__name__)

pytestmark = [
    allure.epic("Tools"),
    allure.feature("PPT 생성"),
    allure.story("PPT 생성 해피 케이스"),
    pytest.mark.jira("KAN-8"),
    pytest.mark.skip(reason="서비스 업데이트로 PPT 생성 기능 삭제됨"),
]

TOPIC        = "AI"
INSTRUCTIONS = "간략하고 빠르게 생성"


# ── fixture ────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def ppt(login_module):
    driver, wait = login_module
    page = PPTPage(driver, wait)
    page.navigate_to_tools()
    page.setup_tool()
    return page


# ── 테스트 케이스 ──────────────────────────────────────────────────

@allure.title("[FHC-049~054] PPT 생성 해피 케이스 (다운로드 포함)")
@allure.severity(allure.severity_level.NORMAL)
def test_ppt_happy_case(ppt):
    """
    [FHC-049~054] PPT 생성 해피 케이스

    전제: 로그인 완료 상태
    단계:
      1. [FHC-049] 'PPT 생성' 메뉴 진입 확인
      2. [FHC-050] 필수 항목(주제) 입력 → [자동 생성] 버튼 활성화 확인
      3. [FHC-051] 선택 항목(지시사항, 슬라이드 수, 섹션 수) 추가 입력 → 버튼 활성화 유지 확인
      4. [FHC-052] 심층조사 모드 토글 OFF 전환 확인
      5. [FHC-053] 자동 생성 버튼 클릭 → 2분 이내 생성 완료 확인
      6. [FHC-054] PPT 다운로드
    기대: 생성 및 다운로드 모두 정상 완료
    """
    with allure.step("[FHC-049] 'PPT 생성' 페이지 진입 확인"):
        logger.info("[FHC-049] PPT 생성 페이지 진입 확인")
        assert ppt.is_on_tool_page(), "PPT 생성 도구 페이지 진입 실패"

    with allure.step("[FHC-050] 필수 항목(주제) 입력"):
        logger.info("[FHC-050] 필수 항목 입력 시작")
        if ppt.has_any_field_value():
            ppt.clear_all_fields()
        ppt.enter_topic(TOPIC)
        assert ppt.is_generate_btn_enabled(), "주제 입력 후 [자동 생성] 버튼 비활성화"

    with allure.step("[FHC-051] 선택 항목 추가 입력"):
        logger.info("[FHC-051] 선택 항목 입력 시작")
        ppt.enter_instructions(INSTRUCTIONS)
        ppt.enter_slides_count()
        ppt.enter_section_count()
        assert ppt.is_generate_btn_enabled(), "선택 항목 입력 후 [자동 생성] 버튼 비활성화"

    with allure.step("[FHC-052] 심층조사 모드 토글 OFF 전환 확인"):
        logger.info("[FHC-052] 심층조사 모드 토글 확인 시작")
        if not ppt.is_deep_research_on():
            ppt.click_deep_research_toggle()
        ppt.click_deep_research_toggle()
        assert not ppt.is_deep_research_on(), "심층조사 모드가 OFF로 전환되지 않음"

    with allure.step("[FHC-053] 자동 생성 버튼 클릭 및 생성 완료 확인"):
        logger.info("[FHC-053] PPT 생성 시작")
        ppt.scroll_to_generate_btn()
        ppt.click_generate()
        assert ppt.is_generated(timeout=120), "2분 이내 PPT 생성 실패"

    with allure.step("[FHC-054] PPT 다운로드"):
        logger.info("[FHC-054] PPT 다운로드 시작")
        assert ppt.download_result(DOWNLOAD_DIR), "PPT 파일 다운로드 실패"

    logger.info("[FHC-049~054] PPT 생성 해피 케이스 완료")
