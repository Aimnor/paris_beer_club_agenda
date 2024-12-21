from .driver_factory import get_driver
import re
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.by import By

def find_all_events(url, driver=get_driver(), timeout=10, delay=1, depth=1):
    # Normalise url
    if re.fullmatch(r'(https?://)?(www.)?facebook.com/([a-zA-Z0-9\-\.\_]+)/?.*', url):
        url = re.sub(
            r'^(https?://)?((www\.)?|(m\.)?)facebook.com/([a-zA-Z0-9\-\.\_]+)/?.*$', r'https://m.facebook.com/\5/events/', url)
    else:
        raise ValueError('Invalid url format')

    driver.get(url)

    time.sleep(delay)
    WebDriverWait(driver, timeout).until(
        ec.visibility_of_element_located((By.ID, "pages_msite_body_contents")))
    time.sleep(delay)

    for _ in range(depth):
        driver.execute_script("window.scrollBy(0, 1080)")
        time.sleep(delay)

    # Remove past events box
    try:
        driver.execute_script(
            "return document.getElementsByClassName('_5zmb')[0].remove();")
    except:
        pass

    links = [str(link.get_attribute("href"))
             for link in driver.find_elements_by_partial_link_text('')]
    links = [link for link in links if re.search("events/[0-9]+", link)]
    links = [re.sub(r'^.*events/([0-9]+).*$',
                    r'https://www.facebook.com/events/\1/', link) for link in links]
    links = list(set(links))

    # Close driver after everything is done
    driver.quit()

    return links
