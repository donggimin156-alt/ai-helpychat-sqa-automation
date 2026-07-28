from config.selenium_imports import By, EC

from config.login_helpers import close_token_banner


class SettingsPage:

    _GEAR_BTN = (By.CSS_SELECTOR, 'button:has(svg[data-testid="gearIcon"])')
    _SETTINGS_MENU_ITEM = (By.CSS_SELECTOR, 'a[role="menuitem"]:has(svg[data-testid="gearIcon"])')
    _ADMIN_URL = "/ai-helpy-chat/admin"

    def __init__(self, driver, wait):
        self.driver = driver
        self.wait = wait

    def navigate_to_settings(self):
        self.wait.until(EC.element_to_be_clickable(self._GEAR_BTN)).click()
        self.wait.until(EC.element_to_be_clickable(self._SETTINGS_MENU_ITEM)).click()
        self.wait.until(EC.url_contains(self._ADMIN_URL))
        close_token_banner(self.driver, self.wait)

    def count_gear_buttons(self) -> int:
        """상단 톱니바퀴(설정 진입) 버튼 개수 반환 — 권한 없는 계정은 0"""
        return len(self.driver.find_elements(*self._GEAR_BTN))
