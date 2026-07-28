# tests/settings/test_settings_organization.py
# 설정 > 조직 구성원 추가 가능 여부 테스트 — FHC-075

import pytest
import logging
import allure
from selenium.webdriver.support.ui import WebDriverWait

from config.settings import DEFAULT_WAIT
from config.browser_factory import make_simple_firefox_driver
from config.login_helpers import do_login, close_token_banner
from pages.settings.settings_general_page import SettingsPage

logger = logging.getLogger(__name__)

pytestmark = [
    allure.epic("Settings"),
    allure.feature("조직 설정"),
]

NON_ADMIN_USER = {
    "id": "elice_3@naver.com",
    "pw": "asd123!!"
}


# ── fixture ────────────────────────────────────────────────────────

@pytest.fixture(scope="module")
def non_admin_login():
    """
    비관리자 계정 로그인 fixture (모듈 공유)

    전제: 권한 없는 계정으로 로그인
    단계:
      1. Firefox 브라우저 실행
      2. 비관리자 계정(elice_3@naver.com)으로 로그인
    """
    driver = make_simple_firefox_driver()
    wait = WebDriverWait(driver, DEFAULT_WAIT)
    do_login(driver, wait, user=NON_ADMIN_USER)
    close_token_banner(driver, wait)
    yield driver, wait
    driver.quit()


# ── 테스트 케이스 ──────────────────────────────────────────────────

@allure.story("비관리자 설정 접근 불가 확인")
@allure.title("[FHC-075] 조직 구성원 추가 가능 여부 테스트")
@allure.severity(allure.severity_level.NORMAL)
def test_FHC_075_non_admin_cannot_access_settings(non_admin_login):
    """
    [FHC-075] 조직 구성원 추가 가능 여부 테스트

    전제: 헬피챗 접속, 로그인 완료 (권한 없는 계정)
    단계:
      1. 헬피챗 사이트 접속
      2. 로그인
      3. 프로필 옆 오른쪽 상단 톱니바퀴 모양 활성화 확인
    기대: 관리자가 아닐 경우 프로필 옆 톱니바퀴 모양이 활성화되지 않아
          조직 구성원 추가할 수 없음
    """
    driver, wait = non_admin_login
    logger.info("[FHC-075] 비관리자 계정 설정 접근 불가 확인 시작")
    gear_count = SettingsPage(driver, wait).count_gear_buttons()
    assert gear_count == 0, f"비관리자 계정에서 톱니바퀴 버튼이 {gear_count}개 표시됨"
    logger.info("[FHC-075] 비관리자 계정 설정 접근 불가 확인 완료")
