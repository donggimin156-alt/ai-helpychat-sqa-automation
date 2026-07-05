# tests/login/test_login.py
# 로그인 E2E 테스트 — FHC-006 ~ FHC-013

import logging
import pytest
import allure

from pages.login.login_page import LoginPage
from pages.logout.logout_page import LogoutPage
from config.settings import LOGIN_URL, TEST_USER

logger = logging.getLogger(__name__)

pytestmark = [
    allure.epic("Login"),
    allure.feature("로그인"),
    allure.story("로그인 동작 확인"),
]

INPUT_EMAIL_INVALID = "email"
INPUT_PWD_INVALID   = "1234"
INPUT_PHONE_INVALID = "123456478"
INPUT_EMAIL_LOCKOUT = "test_login1@elice.io"
INPUT_PWD_LOCKOUT   = "test_login123"


# ── fixtures ───────────────────────────────────────────────────────

@pytest.fixture
def login_page(driver, wait):
    """
    비로그인 상태 로그인 페이지 fixture

    전제: 브라우저 실행 / 쿠키 없는 초기 상태
    단계:
      1. 한글 버전 로그인 페이지(lang=ko-KR) 접속
    """
    driver.get(LOGIN_URL)
    return LoginPage(driver, wait)


# ── 해피패스 ──────────────────────────────────────────────────────

@pytest.mark.smoke
@pytest.mark.jira("KAN-6")
@allure.story("로그인 동작 확인")
@allure.title("[FHC-006] 로그인 동작 확인 (Happy Path)")
@allure.severity(allure.severity_level.CRITICAL)
def test_login_success(login):
    """
    [FHC-006] 로그인 동작 확인 (Happy Path)

    전제: 한글 버전 로그인 페이지 접속 상태
    단계:
      1. 유효한 이메일 입력 (qa5team3-01@elicer.com)
      2. 유효한 비밀번호 입력 (qwer1234!)
      3. 로그인 버튼 클릭
      4. 최초 로그인 시 약관 동의 팝업이 뜨면 동의 후 제출
    기대: URL에 'ai-helpy-chat'이 포함된 메인 페이지로 이동
    """
    logger.info("[FHC-006] 로그인 동작 확인 시작")

    driver, wait = login
    page = LoginPage(driver, wait)

    with allure.step("[FHC-006] 약관 동의 팝업 처리 (최초 로그인 시)"):
        if page.is_terms_popup_displayed():
            page.agree_and_submit()

    with allure.step("[FHC-006] 메인 페이지 이동 확인"):
        assert page.is_login_success(), "로그인 실패 - 메인 페이지 미진입"

    logger.info("[FHC-006] 로그인 동작 확인 완료")


# ── 새드케이스 (해피패스와 독립) ──────────────────────────────────

@allure.story("이메일 유효성 검사")
@allure.title("[FHC-007] 이메일 유효성 검사")
@allure.severity(allure.severity_level.NORMAL)
def test_invalid_email(login_page):
    """
    [FHC-007] 이메일 유효성 검사

    전제: 한글 버전 로그인 페이지 접속 상태
    단계:
      1. 이메일 필드에 '@' 없는 값(qa5team3-01) 입력
    기대: '잘못된 이메일 형식입니다.' 오류 메시지 표시
    """
    logger.info("[FHC-007] 이메일 유효성 검사 시작")

    with allure.step("[FHC-007] 유효하지 않은 이메일 입력"):
        login_page.enter_email(INPUT_EMAIL_INVALID)

    with allure.step("[FHC-007] 이메일 유효성 오류 메시지 확인"):
        assert login_page.is_email_error_displayed(), "이메일 유효성 오류 메시지 미표시"

    logger.info("[FHC-007] 이메일 유효성 검사 완료")


@allure.story("비밀번호 유효성 + 마스킹 확인")
@allure.title("[FHC-008~009] 비밀번호 유효성 검사 + 마스킹 확인")
@allure.severity(allure.severity_level.NORMAL)
def test_password_validation_and_masking(login_page):
    """
    [FHC-008~009] 비밀번호 유효성 검사 + 마스킹 확인

    전제: 한글 버전 로그인 페이지 접속 상태
    단계:
      1. 비밀번호 필드에 8자 미만 값(1234) 입력
      2. 유효성 오류 메시지 확인
      3. 비밀번호 필드 마스킹(type=password) 상태 확인
      4. 눈 아이콘 클릭
      5. 마스킹 해제(type=text) 상태 확인
    기대:
      - '비밀번호는 8자리 이상 입력해주세요.' 오류 메시지 표시
      - 비밀번호 필드 type: 'password' → 'text'로 전환
    """
    logger.info("[FHC-008-009] 비밀번호 유효성 + 마스킹 확인 시작")

    with allure.step("[FHC-008] 비밀번호 유효성 오류 확인"):
        login_page.enter_email("test@example.com")   # 이메일 유효성은 통과, 비밀번호 에러만 발생
        login_page.enter_password(INPUT_PWD_INVALID)
        login_page.click(login_page.LOGIN_BUTTON)  # submit 시도로 유효성 검사 트리거
        assert login_page.is_pwd_error_displayed(), "비밀번호 유효성 오류 메시지 미표시"

    with allure.step("[FHC-009] 비밀번호 마스킹 및 해제 확인"):
        assert login_page.is_pwd_masked(), "비밀번호 마스킹 미적용"
        login_page.toggle_pwd_mask()
        assert login_page.is_pwd_unmasked(), "비밀번호 마스킹 해제 실패"

    logger.info("[FHC-008-009] 비밀번호 유효성 + 마스킹 확인 완료")


@allure.story("비밀번호 찾기 전화번호 유효성")
@allure.title("[FHC-010~011] 비밀번호 찾기 전화번호 유효성 검사")
@allure.severity(allure.severity_level.NORMAL)
def test_find_password_phone_validation(login_page):
    """
    [FHC-010~011] 비밀번호 찾기 → 휴대폰 번호 유효성 검사

    전제: 한글 버전 로그인 페이지 접속 상태
    단계:
      1. '비밀번호를 잊어버리셨나요?' 클릭 → 비밀번호 찾기 페이지 이동
      2. '휴대폰 번호로 찾기' 버튼 클릭
      3. 유효하지 않은 전화번호(123456478) 입력
    기대: '잘못된 번호 형식입니다.' 오류 메시지 표시
    """
    logger.info("[FHC-010-011] 비밀번호 찾기 → 전화번호 유효성 검사 시작")

    with allure.step("[FHC-010] 비밀번호 찾기 페이지 이동"):
        login_page.go_to_forgot_password()

    with allure.step("[FHC-011] 유효하지 않은 전화번호 입력 후 오류 확인"):
        login_page.enter_phone(INPUT_PHONE_INVALID)
        assert login_page.is_phone_error_displayed(), "전화번호 유효성 오류 메시지 미표시"

    logger.info("[FHC-010-011] 비밀번호 찾기 → 전화번호 유효성 검사 완료")


@allure.story("로그인 5회 실패 계정 잠금")
@allure.title("[FHC-012] 로그인 5회 실패 계정 잠금")
@allure.severity(allure.severity_level.NORMAL)
def test_login_lockout(login_page):
    """
    [FHC-012] 로그인 5회 이상 실패 → 계정 잠금 확인

    전제: 한글 버전 로그인 페이지 접속 상태
    단계:
      1. 이메일 필드에 'test_login1@elice.io' 입력
      2. 비밀번호 필드에 잘못된 값(test_login123) 입력
      3. 로그인 버튼 6회 반복 클릭
    기대: '로그인을 여러 번 잘못 시도하셨습니다. 5분 후 시도해 주세요.' 메시지 표시
    """
    logger.info("[FHC-012] 계정 잠금 확인 시작")

    with allure.step("[FHC-012] 잘못된 자격증명으로 6회 로그인 시도"):
        login_page.enter_email(INPUT_EMAIL_LOCKOUT)
        login_page.enter_password(INPUT_PWD_LOCKOUT)
        for _ in range(6):
            login_page.click(login_page.LOGIN_BUTTON)

    with allure.step("[FHC-012] 계정 잠금 메시지 확인"):
        assert login_page.is_lockout_msg_displayed(), "계정 잠금 메시지 미표시"

    logger.info("[FHC-012] 계정 잠금 확인 완료")


@pytest.mark.xfail(reason="FB-001: 로그아웃 후 언어 en-US 초기화 버그")
@allure.story("언어 변경 후 로그인 페이지 언어 확인")
@allure.title("[FHC-013] 언어 변경 후 로그아웃 로그인 페이지 언어")
@allure.severity(allure.severity_level.MINOR)
def test_language_reset_after_logout(login_page, login):
    """
    [FHC-013] 언어 변경 후 로그아웃 시 로그인 페이지 언어 확인

    전제: 한글 버전 로그인 페이지 접속 상태
    단계:
      1. 언어 설정 한국어(ko-KR) 변경
      2. 로그인
      3. 로그아웃
      4. 로그아웃 후 로그인 페이지 언어 확인
    기대: 로그아웃 후 변경된 언어(한국어)의 로그인 페이지로 이동
              (현재 영어로 초기화되는 버그로 인해 FAIL 예상)

    [Bug Report] FB-001
    """
    logger.info("[FHC-013] 언어 초기화 버그 확인 시작")

    with allure.step("[FHC-013] 한국어 설정 후 로그아웃"):
        login_page.select_language("ko-KR")
        driver, wait = login
        logout_page = LogoutPage(driver, wait)
        logout_page.click_profile()
        logout_page.click_logout()

    with allure.step("[FHC-013] 로그아웃 후 언어 확인"):
        current_lang = login_page.get_current_language()
        logger.info(f"[FHC-013] 로그아웃 후 언어: {current_lang}")
        assert current_lang == "ko-KR", f"언어가 초기화됨 (현재: {current_lang})"

    logger.info("[FHC-013] 언어 초기화 버그 확인 완료")
