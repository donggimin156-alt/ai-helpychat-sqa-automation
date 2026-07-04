# conftest.py
# 팀 전체 공통 fixture + 수집 정렬
# 리포팅/로깅/Allure 관련 hook은 plugins/ 패키지로 분리됨

import logging

import pytest

from config.selenium_imports import WebDriverWait
from config.settings import DEFAULT_WAIT, DOWNLOAD_DIR
from config.browser_factory import make_firefox_driver, make_simple_firefox_driver
from config.login_helpers import do_login, do_login_cached

logger = logging.getLogger(__name__)

# pytest 플러그인 등록 (로깅 / Allure / 리포팅)
pytest_plugins = [
    "plugins.logging_plugin",
    "plugins.allure_plugin",
    "plugins.reporting_plugin",
]


# ── 테스트 실행 순서 정렬 (FHC 번호 오름차순) ─────────────────────
def pytest_collection_modifyitems(items):
    """FHC_NNN 번호 기준으로 전체 테스트를 오름차순 정렬"""
    import re

    def _fhc_key(item):
        m = re.search(r'FHC[_-](\d+)', item.nodeid)
        if m:
            return int(m.group(1))
        doc = getattr(item.function, '__doc__', '') or ''
        m = re.search(r'FHC[_-](\d+)', doc)
        if m:
            return int(m.group(1))
        return 9999
    items.sort(key=_fhc_key)


# ── 드라이버 생성/정리 공통 헬퍼 ───────────────────────────────────
def _provide_driver(make_driver):
    """드라이버를 생성해 yield하고, 테스트 종료 시 quit (생성/정리 보일러플레이트 단일화)"""
    _driver = make_driver()
    try:
        yield _driver
    finally:
        _driver.quit()


def _make_tools_driver():
    """tools 전용 드라이버 (다운로드 설정 포함) + 실행 로그"""
    _driver = make_firefox_driver(DOWNLOAD_DIR)
    logger.info("브라우저: FIREFOX 실행 완료")
    return _driver


# ── 브라우저 fixtures (테스트마다 독립 실행) ───────────────────────

@pytest.fixture
def driver():
    """테스트마다 새 Firefox 브라우저 실행"""
    yield from _provide_driver(make_simple_firefox_driver)


@pytest.fixture
def wait(driver):
    return WebDriverWait(driver, DEFAULT_WAIT)


@pytest.fixture
def login(driver, wait):
    """[Before] function scope — 로그인이 필요한 테스트마다 매번 브라우저 시작 + 로그인 실행"""
    do_login(driver, wait)
    return driver, wait


# ── 브라우저 fixtures (모듈 전체 공유) ────────────────────────────

@pytest.fixture(scope="module")
def driver_module():
    """모듈 전체 공유 Firefox 브라우저"""
    yield from _provide_driver(make_simple_firefox_driver)


@pytest.fixture(scope="module")
def wait_module(driver_module):
    return WebDriverWait(driver_module, DEFAULT_WAIT)


@pytest.fixture(scope="module")
def login_module(driver_module):
    """[After] module scope — 테스트 파일(모듈)당 1회만 로그인. 쿠키 캐싱으로 재로그인 속도 개선"""
    _wait = WebDriverWait(driver_module, DEFAULT_WAIT)
    do_login_cached(driver_module, _wait)
    return driver_module, _wait


# ── tools 전용 fixtures (다운로드 디렉터리 설정 포함) ─────────────

@pytest.fixture(scope="module")
def tools_driver_module():
    """tools 테스트 전용 모듈 공유 브라우저 (다운로드 설정 포함)"""
    yield from _provide_driver(_make_tools_driver)


@pytest.fixture
def tools_driver():
    """tools 테스트 전용 독립 브라우저 (다운로드 설정 포함)"""
    yield from _provide_driver(_make_tools_driver)
