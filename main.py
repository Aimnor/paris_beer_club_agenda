import json
from datetime import datetime

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service

import chromedriver_binary

FACEBOOK_URL = "https://www.facebook.com/"
EVENT_ENDPOINT = "/events"

EVENTS_XPATH = "/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div/div/div/div/div/div/div/div/div[3]"
PAST_XPATH = "/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div/div/div/div/div/div/div/div/div[2]/div/div/div/div[2]/a/div/span"
EVENTS_PHP_XPATH = "/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div/div/div/div[1]/div/div/div/div/div[3]/div[1]"
FOLLOWING_PATH = "/html/body/div[1]/div/div[1]/div/div[3]/div/div/div[1]/div[1]/div/div/div[4]/div/div/div/div/div/div/div/div/div[3]"

NOW = datetime.now()


class Event:
    def __init__(self, event_txt: str):
        event_list = event_txt.split("\n")
        if len(event_list) == 5:
            event_list = event_list[:-1]
        elif len(event_list) == 6:
            event_list = event_list[1:-1]
        elif len(event_list) == 7:
            event_list = event_list[1:-1]
            event_list = [event_list[0], event_list[1] + " " + event_list[2], event_list[3], event_list[4]]
        else:
            raise NotImplementedError(f"Can't handle event with size: {len(event_list)}")
        self.name = event_list[1]
        date = event_list[0].replace(",", "").split(' ')
        if len(date) > 5:
            hour = date[4].replace('\u202f', ' ')
            date = f"{NOW.year} {date[1]} {date[2]} {hour}"
            self.date = datetime.strptime(date, "%Y %b %d %I:%M %p")
        else:
            date = f"{NOW.year} {date[1]} {date[2]}"
            self.date = datetime.strptime(date, "%Y %b %d")
        self.address = event_list[2]
        town = event_list[3].split(' ')[-1]
        if not self.address.endswith(town):
            self.address += ", " + town

    def __str__(self) -> str:
        date = self.date.strftime('%d/%m')
        if not (self.date.hour == self.date.minute and self.date.minute == 0):
            date += " à "+self.date.strftime('%H:%M')
        return f"{self.name} le {date} à {self.address}"


def parse_events(events_txt: str):
    if not events_txt:
        return
    events_txt = events_txt.split('Event by')
    return [Event(event_txt) for event_txt in events_txt[:-1]]


def get_events(driver: webdriver.Chrome, url: str):
    if "profile.php?id=" in url:
        url += "&sk=events"
        driver.get(FACEBOOK_URL+url)
        return parse_events(driver.find_elements(By.XPATH, EVENTS_PHP_XPATH)[0].text)
    else:
        url += EVENT_ENDPOINT
        driver.get(FACEBOOK_URL+url)
        if not driver.find_elements(By.XPATH, PAST_XPATH) or driver.find_elements(By.XPATH, PAST_XPATH)[0].text == "Past":
            return []
        return parse_events(driver.find_elements(By.XPATH, EVENTS_XPATH)[0].text)


def get_following(driver):
    """Only works for the firsts followers
    """
    driver.get("https://www.facebook.com/parisbeerclub/following")
    elem = driver.find_elements(By.XPATH, FOLLOWING_PATH)
    soup = BeautifulSoup(elem[0].get_attribute('innerHTML'), )


if __name__ == "__main__":
    service = Service(executable_path='/usr/bin/chromedriver/chromedriver')
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=service, options=options)

    with open("clients.csv", "r") as file_stream:
        lines = file_stream.readlines()
        for line in lines:
            line = line.split(";")
            name = line[0].strip()
            print(name)
            for event in get_events(driver, line[1].strip()):
                if event.date < NOW:
                    continue
                print(f"\t- {event}")
