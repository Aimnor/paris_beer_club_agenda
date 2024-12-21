import browsers
from selenium import webdriver
import os
import logging

logging.getLogger('WDM').setLevel(logging.NOTSET)
os.environ['WDM_LOG'] = '0'
path = r".\\Drivers"


def get_driver():
    from webdriver_manager.chrome import ChromeDriverManager, ChromeType
    from selenium.webdriver.chrome.service import Service as ChromiumService
    from selenium.webdriver.chrome.options import Options
    options = Options()
    options.headless = True
    options.binary_location = '/usr/bin/chromedriver'
    options.add_experimental_option("excludeSwitches", ["enable-logging"])
    return webdriver.Chrome(service=ChromiumService(ChromeDriverManager(chrome_type=ChromeType.CHROMIUM).install()), options=options)

# driver = get_driver()
