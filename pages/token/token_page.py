# pages/token_page.py
# 토큰 사용량 Page Object
# FHC-016 / FHC-017 / FHC-018 / FHC-019

import re
import time

from selenium.webdriver.common.keys import Keys

from config.selenium_imports import By, EC, WebDriverWait

from pages.base_page import BasePage
from config.settings import BASE_URL


class TokenPage(BasePage):

    CHAT_URL  = BASE_URL
    ADMIN_URL = f"{BASE_URL}/admin/general"

    # ========== LNB Locators ==========

    # LNB 토큰 사용량 링크 (설정 > 일반 페이지로 이동)
    LNB_TOKEN_LINK = (
        By.XPATH,
        "//a[contains(@href,'admin/general') or contains(@href,'admin/token')]",
    )

    # LNB 토큰 사용량 텍스트 (예: "5.4M/50M tokens (10.8%)")
    LNB_TOKEN_TEXT = (
        By.XPATH,
        "//*[contains(@href,'admin/general') or contains(@href,'admin/token')]"
        "//*[contains(text(),'token') or contains(text(),'Token') or contains(text(),'토큰')]"
        " | //*[contains(@class,'token') and (contains(text(),'token') or contains(text(),'토큰'))]",
    )

    # ========== 설정 페이지 Locators ==========

    # 토큰 사용량 테이블 (기능별 사용 내역)
    TOKEN_TABLE = (
        By.CSS_SELECTOR,
        "table.MuiTable-root",
    )

    # 토큰 이용 내역 테이블의 행 (증감 비교용)
    TOKEN_TABLE_ROWS = (
        By.CSS_SELECTOR,
        "table.MuiTable-root tr.MuiTableRow-root",
    )

    # '전체 이용 내역' 버튼 (텍스트 기반 — href 기반은 개별 채팅 링크와 혼동될 수 있음)
    ALL_HISTORY_BUTTON = (
        By.XPATH,
        "//button[contains(normalize-space(),'전체 이용 내역') or contains(normalize-space(),'All History')]"
        " | //a[contains(normalize-space(),'전체 이용 내역') or contains(normalize-space(),'All History')]",
    )

    # ========== 채팅 Locators (FHC-017용) ==========

    CHAT_INPUT = (
        By.CSS_SELECTOR,
        "textarea[name='input']",
    )

    RESPONSE_CONTENT = (
        By.CSS_SELECTOR,
        "div.elice-aichat__markdown[data-status='complete']",
    )

    # ========== 토큰 텍스트 파싱 ==========

    def get_lnb_token_text(self) -> str:
        """LNB 토큰 사용량 텍스트 반환 (예: '5.4M/50M tokens (10.8%)')"""
        try:
            el = WebDriverWait(self.driver, 10).until(
                EC.presence_of_element_located(self.LNB_TOKEN_TEXT)
            )
            return el.text.strip()
        except Exception:
            pass
        # JS 폴백: admin 링크 내 텍스트 또는 토큰 관련 텍스트 탐색
        return self.driver.execute_script("""
            var kws = ['token', 'Token', '토큰'];
            var links = Array.from(document.querySelectorAll('a[href*="admin"]'));
            for (var link of links) {
                var txt = (link.innerText || '').trim();
                if (kws.some(function(k){ return txt.includes(k); })) return txt;
            }
            var all = Array.from(document.querySelectorAll('span, p, div'));
            var found = all.find(function(el) {
                var txt = (el.innerText || '').trim();
                return txt.length < 60 && kws.some(function(k){ return txt.includes(k); });
            });
            return found ? found.innerText.trim() : '';
        """) or ""

    def parse_used_tokens(self, text: str) -> float:
        """'5.4M/50M tokens (10.8%)' 에서 사용량(5.4M) → float 변환"""
        match = re.search(r'^([\d.]+)([KMG]?)\s*/', text.strip())
        if not match:
            return 0.0
        num = float(match.group(1))
        unit = match.group(2)
        return num * {'K': 1_000, 'M': 1_000_000, 'G': 1_000_000_000}.get(unit, 1)

    def is_lnb_token_displayed(self) -> bool:
        """LNB에 토큰 사용량이 표시되는지 확인"""
        text = self.get_lnb_token_text()
        self.logger.info(f"LNB 토큰 사용량: '{text}'")
        return bool(text) and "tokens" in text

    # ========== 채팅 메시지 전송 (FHC-017) ==========

    def send_chat_message(self, message: str):
        """채팅 페이지로 이동 후 메시지 전송"""
        self.driver.get(self.CHAT_URL)
        chat_input = self.wait.until(EC.visibility_of_element_located(self.CHAT_INPUT))
        self.js_input(chat_input, message)
        time.sleep(0.3)
        chat_input.send_keys(Keys.RETURN)
        self.logger.info(f"채팅 메시지 전송: '{message}'")

    def wait_for_ai_response(self, timeout: int = 60) -> bool:
        """AI 응답이 완료될 때까지 대기"""
        try:
            WebDriverWait(self.driver, timeout).until(
                EC.url_contains("/ai-helpy-chat/chats/")
            )
            WebDriverWait(self.driver, timeout).until(
                EC.presence_of_element_located(self.RESPONSE_CONTENT)
            )
            self.logger.info("AI 응답 완료 확인")
            return True
        except Exception:
            self.logger.warning("AI 응답 대기 타임아웃")
            return False

    # ========== LNB 토큰 클릭 ==========

    def click_lnb_token(self):
        """LNB 토큰 사용량 링크 클릭"""
        try:
            link = self.wait.until(EC.element_to_be_clickable(self.LNB_TOKEN_LINK))
            self.js_click(link)
            self.logger.info("LNB 토큰 사용량 링크 클릭 완료")
            return
        except Exception:
            pass
        # JS 폴백
        result = self.driver.execute_script("""
            var links = Array.from(document.querySelectorAll('a[href*="admin"]'));
            var kws = ['token', 'Token', '토큰', 'general'];
            var found = links.find(function(a) {
                return kws.some(function(k){ return a.href.includes(k) || (a.innerText||'').includes(k); });
            });
            if (found) { found.click(); return found.href; }
            return 'not-found';
        """)
        if result == 'not-found':
            raise Exception("LNB 토큰 링크를 찾을 수 없습니다")
        self.logger.info(f"LNB 토큰 링크 클릭 완료 (JS): {result}")

    def is_on_settings_general_page(self) -> bool:
        """설정 > 일반 페이지 이동 확인"""
        try:
            self.wait.until(EC.url_contains("/admin/general"))
            self.logger.info("설정 > 일반 페이지 이동 확인")
            return True
        except Exception:
            return False

    def is_token_table_displayed(self) -> bool:
        """기능별 토큰 사용량 테이블 표시 확인"""
        try:
            self.wait.until(EC.presence_of_element_located(self.TOKEN_TABLE))
            self.logger.info("토큰 사용량 테이블 확인")
            return True
        except Exception:
            return False

    def wait_for_token_table(self, timeout: int = None):
        """토큰 사용량 테이블이 DOM에 나타날 때까지 대기"""
        wait = WebDriverWait(self.driver, timeout) if timeout else self.wait
        wait.until(EC.presence_of_element_located(self.TOKEN_TABLE))

    def count_token_history_rows(self) -> int:
        """토큰 이용 내역 테이블의 행 수 반환 (대기 없이 현재 DOM 기준)"""
        return len(self.driver.find_elements(*self.TOKEN_TABLE_ROWS))

    # ========== 전체 이용 내역 ==========

    def click_all_history_button(self):
        """'전체 이용 내역' 버튼 클릭"""
        btn = self.wait.until(EC.element_to_be_clickable(self.ALL_HISTORY_BUTTON))
        self.js_click(btn)
        self.logger.info("전체 이용 내역 버튼 클릭 완료")

    def is_on_history_page(self) -> bool:
        """전체 이용 내역 페이지 이동 확인"""
        try:
            self.wait.until(EC.url_contains("/admin/history"))
            self.logger.info("전체 이용 내역 페이지 이동 확인")
            return True
        except Exception:
            return False
