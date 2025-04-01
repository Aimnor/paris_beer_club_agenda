from selenium import webdriver
from selenium.webdriver.chrome.service import Service as ChromiumService
from webdriver_manager.chrome import ChromeDriverManager
from webdriver_manager.core.os_manager import ChromeType
from selenium.webdriver.chrome.options import Options

import os
import logging

logging.getLogger('WDM').setLevel(logging.NOTSET)
os.environ['WDM_LOG'] = '0'
path = r".\\Drivers"


def get_driver():
    options = Options()
    options.add_argument('--headless=new')
    options.binary_location = '/usr/bin/chromedriver'
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    options.add_argument("start-maximized")
    driver = webdriver.Chrome(service=ChromiumService(ChromeDriverManager(
        chrome_type=ChromeType.CHROMIUM).install()), options=options)
    return driver


driver = get_driver()
