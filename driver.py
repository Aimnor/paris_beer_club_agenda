from bs4 import BeautifulSoup

from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.common.exceptions import WebDriverException


class Driver:
    def __init__(self, chromedriver_executable_path: str = "/usr/bin/chromedriver"):
        service = Service(executable_path=chromedriver_executable_path)
        options = webdriver.ChromeOptions()
        self._driver = webdriver.Chrome(service=service, options=options)

    def get_soup(self, url: str) -> BeautifulSoup:
        self._driver.get(url)
        soup = BeautifulSoup(self._driver.page_source, 'html.parser')
        if "Ce contenu n’est pas disponible pour le moment" in soup.text or "This content isn't available right now" in soup.text:
            raise ConnectionError(f"Can't display {url}")

        if "Log In" in soup.text:
            deny_cookies = "Decline optional cookies"
            close = "Close"
        else:
            deny_cookies = "Refuser les cookies optionnels"
            close = "Fermer"

        buttons = self._driver.find_elements(
            By.XPATH, f"//div[@role = 'button' and @aria-label = '{deny_cookies}']")
        for button in buttons:
            try:
                button.click()
            except WebDriverException:
                pass
        buttons = self._driver.find_elements(
            By.XPATH, f"//div[@role = 'button' and @aria-label = '{close}']")
        for button in buttons:
            try:
                button.click()
            except WebDriverException:
                pass
        return BeautifulSoup(self._driver.page_source, 'html.parser')
