# plugins/reporting_plugin.py
# 테스트 결과 리포팅 — CLI 옵션, 실패 로깅 + Jira 이슈 자동 생성, Discord 결과 전송

import logging
import os
import re
from datetime import datetime

import requests
import pytest
from dotenv import load_dotenv

from utils.jira_helper import (
    create_jira_bug_ticket,
    attach_image_to_jira,
    add_comment_to_issue,
    transition_issue_to_done,
)

load_dotenv()

logger = logging.getLogger(__name__)

# Discord 웹훅 URL — .env에서 주입 (소스에 하드코딩 금지)
DISCORD_WEBHOOK_URL = os.getenv("DISCORD_WEBHOOK_URL")


# ── CLI 옵션 ───────────────────────────────────────────────────────
def pytest_addoption(parser):
    parser.addoption(
        "--discord",
        action="store_true",
        default=False,
        help="테스트 완료 후 Discord로 결과 전송",
    )
    parser.addoption(
        "--open",
        action="store_true",
        default=False,
        help="테스트 완료 후 HTML 리포트를 브라우저로 열기",
    )
    parser.addoption(
        "--jira",
        action="store_true",
        default=False,
        help="실패 테스트를 Jira 등록"
    )


# ── 테스트 실패 자동 로깅 + Jira 이슈 생성 및 스크린샷 첨부 Hook ──
@pytest.hookimpl(tryfirst=True, hookwrapper=True)
def pytest_runtest_makereport(item, call):
    outcome = yield
    report = outcome.get_result()

    # ── 로그 처리 ─────────────────────────────
    if report.when == "call":
        _logger = logging.getLogger(item.module.__name__)

        if report.failed:
            # ① 로그 기록
            msg = str(report.longrepr)
            match = re.search(r'AssertionError:\s*(.+)', msg)
            fail_msg = match.group(1).strip() if match else msg.splitlines()[-1].strip()
            _logger.error(f"❌ {item.name} | {fail_msg}")

        elif report.passed:
            _logger.info(f"✅ {item.name}")

        elif report.skipped:
            reason = getattr(report, 'wasxfail', None) or str(report.longrepr)
            _logger.warning(f"⚠️  {item.name} | {reason}")

    # ── Jira 처리 ────────────────────────────
    if report.when != "call":
        return

    jira_enabled = item.config.getoption("--jira")
    if not jira_enabled:
        return

    # xfail 제외
    if hasattr(report, "wasxfail"):
        return

    # driver 탐색
    driver = (
        item.funcargs.get("driver")
        or item.funcargs.get("driver_module")
        or item.funcargs.get("tools_driver")
        or item.funcargs.get("tools_driver_module")
    )

    current_url = "URL 확인 실패"
    browser_name = "unknown"

    if driver:
        try:
            current_url = driver.current_url
        except Exception:
            pass
        try:
            browser_name = driver.capabilities.get("browserName")
        except Exception:
            pass

    # @pytest.mark.jira('ISSUE-KEY') 마커 확인
    jira_marker = item.get_closest_marker("jira")
    linked_issue_key = jira_marker.args[0] if jira_marker and jira_marker.args else None

    test_file = item.location[0]

    if report.failed:
        error_message = str(call.excinfo.value)

        if linked_issue_key:
            # ── 연결된 이슈에 실패 코멘트 + 스크린샷 추가 ──
            comment_body = (
                f"*[자동화 테스트 실패]* {item.name}\n\n"
                f"{{panel:title=실패 상세}}\n"
                f"*파일:* {test_file}\n"
                f"*브라우저:* {browser_name}\n"
                f"*URL:* {current_url}\n"
                f"*오류:* {error_message}\n"
                f"{{panel}}"
            )
            add_comment_to_issue(linked_issue_key, comment_body)

            if driver:
                try:
                    screenshot = driver.get_screenshot_as_png()
                    attach_image_to_jira(linked_issue_key, screenshot)
                except Exception as e:
                    logger.warning(f"스크린샷 첨부 실패: {e}")

        else:
            # ── 마커 없는 실패 → 새 버그 티켓 생성 (기존 동작) ──
            summary = f"[자동화 테스트 실패] {item.name}"
            description = (
                f"자동화 테스트 실패\n\n"
                f"[Test Case]\n{item.name}\n\n"
                f"[Test File]\n{test_file}\n\n"
                f"[Browser]\n{browser_name}\n\n"
                f"[URL]\n{current_url}\n\n"
                f"[Error]\n{error_message}"
            )
            new_key = create_jira_bug_ticket(summary=summary, description=description)

            if new_key and driver:
                try:
                    screenshot = driver.get_screenshot_as_png()
                    attach_image_to_jira(new_key, screenshot)
                except Exception as e:
                    logger.warning(f"스크린샷 첨부 실패: {e}")

    elif report.passed and linked_issue_key:
        # ── 연결된 이슈 통과 → Done 전이 + 코멘트 ──
        comment_body = (
            f"*[자동화 테스트 통과]* {item.name}\n\n"
            f"브라우저: {browser_name} | URL: {current_url}"
        )
        add_comment_to_issue(linked_issue_key, comment_body)
        transition_issue_to_done(linked_issue_key)


# ── pytest 종료 시 Discord 결과 전송 ──────────────────────────────
def pytest_terminal_summary(terminalreporter, exitstatus, config):
    if not config.getoption("--discord", default=False):
        return

    passed = len(terminalreporter.stats.get('passed', []))
    failed = len(terminalreporter.stats.get('failed', []))
    error  = len(terminalreporter.stats.get('error', []))
    total  = passed + failed + error
    date   = datetime.now().strftime("%Y-%m-%d %H:%M")

    args = [a for a in config.args if not a.startswith("-")]
    if args:
        test_name = ", ".join(os.path.basename(a.rstrip("/\\")) for a in args) + " 테스트 결과"
    else:
        test_name = "전체 테스트 결과"

    config._discord_message = f"""🚀 {test_name}
테스트 일자: {date}
✅ 성공: {passed}건
❌ 실패: {failed}건
총: {total}건"""


def pytest_unconfigure(config):
    if not config.getoption("--discord", default=False):
        return

    message = getattr(config, '_discord_message', '')
    screenshot_bytes = None

    try:
        import threading, http.server, socket, time
        from selenium import webdriver
        from selenium.webdriver.firefox.options import Options as FirefoxOptions

        with socket.socket() as s:
            s.bind(('', 0))
            port = s.getsockname()[1]

        class _Handler(http.server.SimpleHTTPRequestHandler):
            def __init__(self, *args, **kwargs):
                super().__init__(*args, directory="allure-report", **kwargs)
            def log_message(self, *args):
                pass

        server = http.server.HTTPServer(('localhost', port), _Handler)
        t = threading.Thread(target=server.serve_forever)
        t.daemon = True
        t.start()

        opts = FirefoxOptions()
        opts.add_argument("--headless")
        driver = webdriver.Firefox(options=opts)
        try:
            driver.get(f"http://localhost:{port}/index.html")
            driver.set_window_size(1400, 900)
            time.sleep(4)
            screenshot_bytes = driver.get_screenshot_as_png()
        finally:
            driver.quit()
            server.shutdown()

    except Exception as e:
        logger.warning(f"Allure 리포트 스크린샷 실패: {e}")

    if not DISCORD_WEBHOOK_URL:
        logger.warning("DISCORD_WEBHOOK_URL 미설정 — Discord 전송 건너뜀")
        return

    try:
        if screenshot_bytes:
            requests.post(
                DISCORD_WEBHOOK_URL,
                data={"content": message},
                files={"file": ("report.png", screenshot_bytes, "image/png")},
                timeout=30
            )
        else:
            requests.post(DISCORD_WEBHOOK_URL, json={"content": message}, timeout=10)
    except Exception as e:
        logger.warning(f"Discord 전송 실패: {e}")
