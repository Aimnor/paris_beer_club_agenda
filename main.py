from __future__ import annotations

import re
import json
import sys
from datetime import timedelta, datetime
from collections import OrderedDict

from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.chrome.service import Service


FACEBOOK_URL = "https://www.facebook.com/"
PRO_EVENT_ENDPOINT = "events"
NOT_PRO_EVENT_ENDPOINT = "&sk=events"

DATE_PATTERN = re.compile(
    r"[A-Z][a-z][a-z], ([A-Z][a-z][a-z] \d\d?) at (\d\d?:\d\d)[^a-zA-Z0-1]([A-Z]M) [A-Z][A-Z][A-Z]T")

LINK_PATTERN = re.compile(rf"{FACEBOOK_URL}{PRO_EVENT_ENDPOINT}.*")

NOW = datetime.now()


class Event:
    def __init__(self, date: datetime, name: str, address: str, subscriber: str, organizers: str, link=str):
        self.name = name
        self.date = date
        self.address = address
        self.subscriber = subscriber
        if organizers == subscriber:
            self.organizer = None
        self.link = link

    def _get_pretty_date(self) -> str:
        date = self.date.strftime('%d/%m')
        if not (self.date.hour == self.date.minute and self.date.minute == 0):
            date += " à "+self.date.strftime('%H:%M')
        return date

    def __str__(self) -> str:
        return f"{self.name} le {self._get_pretty_date()} à {self.address} par {self.subscriber}"

    def __repr__(self) -> str:
        return f"{self.name} {self._get_pretty_date()} {self.subscriber}"

    def to_dict(self) -> dict:
        return {"name": self.name, "date": self._get_pretty_date(), "address": self.address, "organizer": self.subscriber, "link": self.link}

    def to_json(self) -> str:
        return json.dumps(self.to_dict(), indent=4, ensure_ascii=False)

    def to_markdown(self) -> str:
        if not self.link:
            return str(self)
        return f"[{self.name}]({self.link}) le {self._get_pretty_date()} à {self.address} par {self.subscriber}"

    def __eq__(self, other: Event):
        return self.name == other.name and self.date == other.date and self.address == other.address and self.subscriber == other.subscriber


def get_even_elem(elem, date_text) -> BeautifulSoup:
    if elem.parent.text == date_text:
        return get_even_elem(elem.parent, date_text)
    return elem.parent


def get_events(driver: webdriver.Chrome, subscriber: str, url: str) -> list[Event]:
    events = []
    if "profile.php?id=" in url:
        url += "/"+NOT_PRO_EVENT_ENDPOINT
    else:
        url += "/"+PRO_EVENT_ENDPOINT

    driver.get(FACEBOOK_URL+url)
    soup = BeautifulSoup(driver.page_source, 'html.parser')
    for elem in soup.find_all('span'):
        match = DATE_PATTERN.match(elem.text)
        if match:

            event_elem = get_even_elem(elem, elem.text)

            links = event_elem.find_all('a', href=LINK_PATTERN)

            link = ""
            if links:
                link = links[0]['href']
            date = datetime.strptime(f'{NOW.year} '+' '.join(match.groups()), '%Y %b %d %I:%M %p')
            elem_dict = event_elem.get_text(separator=';').split(";")
            elem_dict.remove(elem.text)
            event = Event(date=date, name=elem_dict[0],
                          address=elem_dict[1], subscriber=subscriber, organizers=elem_dict[-1], link=link)
            if event not in events:
                events.append(event)
    return events


def get_subscribers(driver) -> dict[str, list[Event]]:
    # Only works for the firsts followers
    # driver.get("https://www.facebook.com/parisbeerclub/following")
    # elem = driver.find_elements(By.XPATH, FOLLOWING_PATH)
    # soup = BeautifulSoup(elem[0].get_attribute('innerHTML'), )

    with open("subscribers.csv", "r", encoding="utf-8") as file_stream:
        subscribers_data = file_stream.readlines()
    subscribers = {}
    for url in subscribers_data:
        if not url.strip():
            continue
        url = url.split(";")
        name = url[0].strip()
        assert url and " " not in url, f"{url} is not a valid url"
        subscribers[name] = get_events(driver, name, url[1].strip())
    return subscribers


def get_beer_agenda(start: datetime, stop: datetime):
    service = Service(executable_path='/usr/bin/chromedriver/chromedriver')
    options = webdriver.ChromeOptions()
    driver = webdriver.Chrome(service=service, options=options)

    subscribers = get_subscribers(driver)
    dates = [start + timedelta(days=x) for x in range((stop-start).days)]
    beer_agenda = OrderedDict()
    for date in dates:
        beer_agenda[date.strftime('%A %-d %B')] = []
    json_subscribers = {}
    for subscriber, events in subscribers.items():
        json_subscribers[subscriber] = []
        if not events:
            continue
        for event in events:
            event_dict = event.to_dict()
            json_subscribers[subscriber].append(event_dict)
            if event.date <= stop and event.date >= start:
                beer_agenda[event.date.strftime('%A %-d %B')].append(event)
    beer_agenda_txt = '\n'.join([f"# {str_date}\n"+"\n".join([f"- {event.to_markdown()}" for event in events])
                                 for str_date, events in beer_agenda.items()])
    with open("output/subscribers.json", "w", encoding="utf-8") as file_stream:
        json.dump(json_subscribers, file_stream, indent=4, ensure_ascii=False)
    # with open("output/beer_agenda.json", "w", encoding="utf-8") as file_stream:
    #     json.dump(beer_agenda, file_stream, indent=4, ensure_ascii=False)
    with open("output/beer_agenda.md", "w", encoding="utf-8") as file_stream:
        file_stream.write(beer_agenda_txt)


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python main.py start_date stop_date")
        sys.exit(1)
    start = datetime.strptime(sys.argv[1], "%Y_%m_%d")
    stop = datetime.strptime(sys.argv[2], "%Y_%m_%d")
    get_beer_agenda(start, stop)
