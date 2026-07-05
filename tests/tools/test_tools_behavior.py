# tests/test_tools_02.py
# '행동특성 및 종합의견' 도구 E2E 테스트 — FHC-037 ~ FHC-044

import logging
import pytest
import allure

from pages.tools.tools_behavior_page import BehaviorPage
from config.settings import DOWNLOAD_DIR

logger = logging.getLogger(__name__)

pytestmark = [
    allure.epic("Tools"),
    allure.feature("행동특성 및 종합의견"),
    allure.story("행동특성 및 종합의견 생성 해피 케이스"),
]

SCHOOL_LEVEL  = "중학교"
NAME_TEXT     = "포커스 1차 프로젝트"
REQUEST_TEXT  = "엘리스 부트 캠프"


# ── fixture ────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def behavior(tools_driver_module):
    """
    BehaviorPage fixture (모듈 공유)

    전제: tools_driver_module fixture로 로그인 완료 상태
    단계:
      1. tools_driver_module에서 driver 수신 → BehaviorPage 반환
    """
    page = BehaviorPage(tools_driver_module)
    page.login()
    return page


# ── 테스트 케이스 ──────────────────────────────────────────────────

@allure.title("[FHC-037~044] 행동특성 및 종합의견 생성 해피 케이스")
@allure.severity(allure.severity_level.NORMAL)
def test_behavior_happy_case(behavior):
    """
    [FHC-037~044] 행동특성 및 종합의견 생성 해피 케이스

    전제: 로그인 완료 상태
    단계:
      1. [FHC-037] LNB > '도구' 탭 클릭 → '행동특성 및 종합의견' 도구 확인 및 클릭
      2. [FHC-038] 수업 정보 필수 항목 입력 (교과급) → '다음으로' 버튼 활성화
      3. [FHC-039] '다음으로' 버튼 클릭 → '학생 정보 입력 및 생성' 페이지 이동
      4. [FHC-040] 이전 입력 데이터(수업 정보) 반영 확인
      5. [FHC-041~042] 학생 이름 입력 및 인성·태도 키워드 선택 · 저장
      6. [FHC-043] [학생 추가] 버튼 클릭 → 새 학생 목록 생성
      7. [FHC-044] [생성 결과 받기] 버튼 클릭 → xlsx 파일 다운로드
    기대: 전체 시나리오 정상 완료
    """
    with allure.step("[FHC-037] '도구' 탭 클릭 → 도구 목록 표시"):
        logger.info("[FHC-037] 도구 목록 표시 확인 시작")
        behavior.navigate_to_tools()
        assert behavior.is_tools_list_displayed(), \
            "도구 목록 페이지에 도구 카드가 표시되지 않았습니다"

    with allure.step("[FHC-037] '행동특성 및 종합의견' 도구 클릭"):
        logger.info("[FHC-037] 행동특성 및 종합의견 도구 클릭 시작")
        behavior.click_tool_menu(BehaviorPage.TOOL_NAME)
        assert behavior.is_on_tool_page(), \
            "행동특성 및 종합의견 도구 페이지로 이동하지 못했습니다"

    with allure.step("[FHC-038] 수업 정보 입력 준비 (초기화)"):
        logger.info("[FHC-038] 수업 정보 입력 준비 시작")
        behavior.reset_inputs()
        assert behavior.is_class_info_tab_visible(), \
            "초기화 완료 후 수업 정보 입력 탭이 표시되지 않았습니다"

    with allure.step("[FHC-038] 수업 정보 입력 탭 이동 및 교과급 선택"):
        logger.info("[FHC-038] 수업 정보 입력 탭 이동 및 교과급 선택 시작")
        behavior.click_class_info_tab()
        assert behavior.is_school_level_combobox_visible(), \
            "수업 정보 입력 화면(학교급 콤보박스)이 표시되지 않았습니다"
        behavior.select_school_level(SCHOOL_LEVEL)
        assert behavior.is_next_button_enabled(), \
            f"학교급 '{SCHOOL_LEVEL}' 선택 후 '다음으로' 버튼이 활성화되지 않았습니다"

    with allure.step("[FHC-039~040] '다음으로' 버튼 클릭 → '학생 정보 입력 및 생성' 페이지 이동 / 이전 입력 데이터 반영 확인"):
        logger.info("[FHC-039] 다음으로 버튼 클릭 시작")
        behavior.click_next()
        behavior.handle_modify_modal()
        assert behavior.is_student_tab_visible(), \
            "학생 정보 입력 및 생성 페이지로 이동하지 못했습니다"

    with allure.step("[FHC-041] 학생 이름 입력"):
        logger.info("[FHC-041] 학생 이름 입력 시작")
        behavior.ensure_student_row_exists()
        behavior.enter_student_name(NAME_TEXT)
        assert behavior.is_student_name_entered(NAME_TEXT), \
            f"학생 이름 '{NAME_TEXT}'이 입력 필드에 반영되지 않았습니다"

    with allure.step("[FHC-041~042] 인성·태도 키워드 선택 및 저장"):
        logger.info("[FHC-041~042] 인성·태도 키워드 선택 및 저장 시작")
        behavior.open_keyword_modal()
        behavior.select_character_keyword()
        behavior.save_keyword_modal()
        if REQUEST_TEXT:
            behavior.enter_request_text(REQUEST_TEXT)
        assert behavior.is_result_button_visible(), \
            "키워드 저장 후 '생성 결과 받기' 버튼이 표시되지 않았습니다"

    with allure.step("[FHC-043] '학생 추가' 버튼 클릭 → 새 학생 목록 생성"):
        logger.info("[FHC-043] 학생 추가 버튼 클릭 시작")
        behavior.trigger_generation()

    with allure.step("[FHC-044] '생성 결과 받기' 버튼 클릭 → xlsx 파일 다운로드"):
        logger.info("[FHC-044] 생성 결과 받기 버튼 클릭 시작")
        result = behavior.download_result(DOWNLOAD_DIR)
        assert result, "xlsx 결과 파일 다운로드에 실패했습니다"

    logger.info("[FHC-037~044] 행동특성 및 종합의견 생성 해피 케이스 완료")
