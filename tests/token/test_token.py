# tests/test_token_01.py
# 토큰 사용량 E2E 테스트 — FHC-018 ~ FHC-021

import time

import pytest
import allure

from pages.token.token_page import TokenPage
from pages.tools.base_tool_page import BaseToolPage

TEST_MESSAGE = "안녕하세요, 토큰 사용량 테스트입니다."

pytestmark = [
    allure.epic("Token"),
    allure.feature("토큰 사용량"),
]


# ── fixture ────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def token(tools_driver_module):
    """
    TokenPage fixture (모듈 공유)

    전제: tools_driver_module fixture로 로그인 완료 상태
    단계:
      1. tools_driver_module에서 driver 수신 → TokenPage 반환
    """
    page = TokenPage(tools_driver_module)
    base = BaseToolPage(tools_driver_module)
    base.login()
    return page


# ── 테스트 케이스 ──────────────────────────────────────────────────

@allure.story("LNB 토큰 사용량 표시 확인")
@allure.title("[FHC-018] LNB 토큰 사용량 표시 확인")
@allure.severity(allure.severity_level.NORMAL)
def test_lnb_token_displayed(token):
    """
    [FHC-018] LNB 토큰 사용량 표시 확인

    전제: 로그인 한 상태
    단계:
      1. LNB > '토큰 사용량' 메뉴 확인
    기대: 내가 사용한 토큰량이 LNB에 반영된다
    """
    token.driver.get(token.CHAT_URL)
    assert token.is_lnb_token_displayed(), \
        "LNB에 토큰 사용량이 표시되지 않았습니다"


@allure.story("AI 대화 후 토큰 사용량 증가")
@allure.title("[FHC-019] AI 대화 후 토큰 사용량 증가 확인")
@allure.severity(allure.severity_level.NORMAL)
def test_token_increases_after_chat(token):
    """
    [FHC-019] AI 대화 후 토큰 사용량 증가 확인

    전제: 로그인 한 상태
    단계:
      1. 이용 내역 페이지 행 수 기록
      2. AI를 통한 대화 진행
      3. 이용 내역 페이지 새로고침 후 행 수 비교
    기대: 토큰 이용 내역 행 수가 증가한다
    """
    token.driver.get(token.ADMIN_URL)
    time.sleep(1)
    token.click_all_history_button()
    token.wait_for_token_table()
    before_rows = token.count_token_history_rows()
    before_text = token.get_lnb_token_text()

    token.send_chat_message(TEST_MESSAGE)
    assert token.wait_for_ai_response(), "AI 응답 생성 실패"

    token.driver.get(token.ADMIN_URL)
    time.sleep(1)
    token.click_all_history_button()
    token.wait_for_token_table(timeout=15)
    time.sleep(2)
    after_rows = token.count_token_history_rows()
    after_text = token.get_lnb_token_text()

    assert after_rows > before_rows, \
        f"대화 후 토큰 이용 내역이 증가하지 않았습니다 (전: {before_rows}행 → 후: {after_rows}행)"


@allure.story("LNB 토큰 클릭 설정 페이지 이동")
@allure.title("[FHC-020] LNB 토큰 클릭 → 설정 페이지 이동")
@allure.severity(allure.severity_level.NORMAL)
def test_lnb_token_click_goes_to_settings(token):
    """
    [FHC-020] LNB 토큰 클릭 → 설정 페이지 이동 확인

    전제: 로그인 한 상태
    단계:
      1. LNB > '토큰 사용량' 메뉴 클릭
    기대: 설정 > 일반 > 토큰 사용 상세 페이지로 이동한다
    """
    token.driver.get(token.CHAT_URL)
    token.click_lnb_token()
    assert token.is_on_settings_general_page(), \
        "토큰 사용량 클릭 후 설정 > 일반 페이지로 이동하지 않았습니다"
    assert token.is_token_table_displayed(), \
        "설정 페이지에 토큰 사용량 테이블이 표시되지 않았습니다"


@allure.story("전체 이용 내역 버튼")
@allure.title("[FHC-021] '전체 이용 내역' 버튼 클릭")
@allure.severity(allure.severity_level.NORMAL)
def test_all_history_button(token):
    """
    [FHC-021] '전체 이용 내역' 버튼 클릭 → 이동 확인

    전제: 설정 > 일반 > 토큰 사용 상세 페이지
    단계:
      1. 하단 '전체 이용 내역' 버튼 클릭
    기대: '전체 이용 내역' 페이지로 이동한다
    """
    token.click_all_history_button()
    assert token.is_on_history_page(), \
        "'전체 이용 내역' 클릭 후 이용 내역 페이지로 이동하지 않았습니다"
