from .driver_factory import get_driver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.common.exceptions import NoSuchElementException, StaleElementReferenceException
import time
import re
from datetime import datetime, timedelta
from dateutil.parser import *


def get_event_details(url, driver=get_driver(), timeout=10, delay=1, depth=1):
    # Normalise url
    if re.fullmatch(r'(https?://)?((www\.)?|(m\.)?)facebook.com/events/([0-9]+)/?.*', url):
        url = re.sub(
            r'^(https?://)?((www\.)?|(m\.)?)facebook.com/events/([0-9]+)/?.*$', r'https://m.facebook.com/events/\5/', url)
    else:
        raise ValueError('Invalid url format')
    driver.get(url)

    WebDriverWait(driver, timeout).until(
        ec.visibility_of_element_located((By.ID, "event_tabs")))
    time.sleep(delay)

    for _ in range(depth):
        driver.execute_script("window.scrollBy(0, 1080)")
        time.sleep(delay)

    # Click read more buttom
    try:
        driver.execute_script(
            'document.querySelectorAll(\'[data-sigil="more"]\')[0].click()')
    except:
        pass

    event = {
        "id": re.sub(r'^.*events/([0-9]+).*$', r'\1', url),
        "url": url,
        "title": driver.find_element_by_class_name("_31y8").text,
        "time_start": None,
        "time_finish": None,
        "description": None,
        "location": None,
        "hosts": [],
        "image_url": None,
        "category": None
    }

    try:
        event["description"] = driver.find_element_by_class_name(
            "text_exposed").text

    except NoSuchElementException:
        event["description"] = "No description"

    time_string = driver.find_elements_by_class_name("_52je")[0].text

    def parse_fb_time(time_string):
        # Returns a datetime start and a datetime end
        start = end = None
        # Wednesday, 13 April 2022 from 11:30-12:30 UTC+10
        if re.fullmatch(r'[MTWFS][a-z]{2,5}day, [0-9]+ [A-Z][a-z]+ [0-9]{4} from [0-9]{2}:[0-9]{2}-[0-9]{2}:[0-9]{2} UTC[+-][0-9]{1,2}', time_string):
            time_string = re.sub(
                r'[MTWFS][a-z]{2,5}day, ([0-9]+ [A-Z][a-z]+ [0-9]{4}) from ([0-9]{2}:[0-9]{2})-([0-9]{2}:[0-9]{2}) UTC[+-][0-9]{1,2}', r'\1 at \2 to \1 at \3', time_string)
            start, end = [parse(t) for t in time_string.split(' to ')]
        # 25 Mar at 01:00 - 8 Apr at 00:00 UTC+11
        elif re.fullmatch(r'[0-9]{1,2} [A-Z][a-z]{2} at [0-9]{2}:[0-9]{2} . [0-9]{1,2} [A-Z][a-z]{2} at [0-9]{2}:[0-9]{2} UTC[+-][0-9]{1,2}', time_string):
            time_string = re.sub(
                r'([0-9]{1,2} [A-Z][a-z]{2} at [0-9]{2}:[0-9]{2}) . ([0-9]{1,2} [A-Z][a-z]{2} at [0-9]{2}:[0-9]{2}) UTC[+-][0-9]{1,2}', r'\1 to \2', time_string)
            start, end = [parse(t) for t in time_string.split(' to ')]
        # Monday, 16 May 2022 at 18:30 UTC+10
        elif re.fullmatch(r'[MTWFS][a-z]{2,5}day, [0-9]+ [A-Z][a-z]+ [0-9]{4} at [0-9]{2}:[0-9]{2} UTC[+-][0-9]{1,2}', time_string):
            time_string = re.sub(
                r'[MTWFS][a-z]{2,5}day, ([0-9]+ [A-Z][a-z]+ [0-9]{4}) at ([0-9]{2}:[0-9]{2}) UTC[+-][0-9]{1,2}', r'\1 at \2', time_string)
            start = end = parse(time_string)
        # Until 31 May · UTC+11
        # 2 dates left · UTC+10
        elif re.fullmatch(r'Until [0-9]{1,2} [A-Z][a-z]+ . UTC[+-][0-9]{1,2}', time_string) or re.fullmatch(r'[0-9]+ dates left .*', time_string):
            # Recurring event, not supported
            raise TypeError("Recurring event not supported")
        # 14 Apr at 15:00 – 17:00 · UTC+11
        elif re.fullmatch(r'[0-9]{1,2} [A-Z][a-z]{2} at [0-9]{2}:[0-9]{2} . [0-9]{2}:[0-9]{2} . UTC[+-][0-9]{1,2}', time_string):
            # Recurring event but only one left
            curr_year = datetime.now().year
            time_string = re.sub(r'([0-9]{1,2} [A-Z][a-z]{2}) at ([0-9]{2}:[0-9]{2}) . ([0-9]{2}:[0-9]{2}) . UTC[+-][0-9]{1,2}',
                                 rf'\1 {curr_year} at \2 to \1 {curr_year} at \3', time_string)
            start, end = [parse(t) for t in time_string.split(' to ')]
        else:
            print(time_string)
            raise ValueError('Invalid time format')

        return datetime.isoformat(start), datetime.isoformat(end)

    event["time_start"], event["time_finish"] = parse_fb_time(time_string)

    try:
        event["location"] = driver.find_elements_by_class_name("fbEventInfoText")[
            1].text
    except:
        pass

    try:
        event["categories"] = [driver.find_element_by_xpath(
            "//li[@class='_63ep _63eq']").text]
    except:
        pass

    # Get event image
    try:
        classes = ['_537g _403j']
        for html_class in classes:
            try:
                event["image_url"] = driver.find_element_by_xpath(
                    f"//img[@class='{html_class} img']").get_attribute("src")
                break
            except NoSuchElementException:
                pass
    except NoSuchElementException:
        pass
    except StaleElementReferenceException:
        pass

    # Navigate to modern page
    url = re.sub(
        r'^(https?://)?((www\.)?|(m\.)?)facebook.com/events/([0-9]+)/?.*$', r'https://facebook.com/events/\5/', url)
    event["url"] = url
    driver.get(url)
    time.sleep(delay)

    hosted_by = driver.find_elements_by_xpath("//div[@class='discj3wi ihqw7lf3']")
    hosts = hosted_by[0]
    for h in hosted_by[1:]:
        if h.text.startswith("Hosts"):
            hosts = h
            break

    hosts = hosts.find_elements_by_partial_link_text('')
    host_urls = []
    for host in hosts:
        host_url = host.get_attribute('href')
        if (re.match(r'.*[^#]$', host_url)) and 'www.facebook.com/events/' not in host_url:
            host_urls.append(host_url)
    host_urls = list(set(host_urls))

    for host_url in host_urls:
        try:
            driver.get(host_url)
            time.sleep(delay)

            info = {
                "id": host_url.split('/')[3],
                "name": driver.find_element_by_class_name("tr9rh885").find_elements_by_xpath("//h1[@class='gmql0nx0 l94mrbxd p1ri9a11 lzcic4wl']")[0].text,
                "url": host_url,
            }

            event["hosts"].append(info)
        except Exception as e:
            pass

    
    time.sleep(delay)

    # driver.close()
    driver.quit()

    return event
