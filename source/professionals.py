
from __future__ import annotations

import os
import re
import json
from datetime import datetime

from bs4 import BeautifulSoup
from selenium import webdriver

from alive_progress import alive_it

from .driver import Driver

FACEBOOK_URL = "https://www.facebook.com/"

WORD_PATTERN = re.compile(r"\w+")

DAY_FORMAT = '%Y %m %d'
TODAY = datetime.strptime(datetime.now().strftime(DAY_FORMAT), DAY_FORMAT)


class Event:
    DATE_DUMP_FORMAT = '%Y/%m/%d %H:%M'
    FACEBOOK_DATE_PATTERN = re.compile(
        r"[A-Z][a-z][a-z], ([A-Z][a-z][a-z] \d\d?) at (\d\d?:\d\d)[^a-zA-Z0-1]([A-Z]M) [A-Z][A-Z][A-Z]T")
    FACEBOOK_LINK_PATTERN = re.compile(rf"{FACEBOOK_URL}events.*")

    def __init__(self, date: datetime | str, name: str, address: str, professional: Professional, link=str):
        self.name = Event._get_beautiful_name(name)
        if isinstance(date, str):
            date = datetime.strptime(date, Event.DATE_DUMP_FORMAT)
        self.date = date
        self.professional = professional
        if address == professional.name:
            self.address = professional.address
        else:
            self.address = address.strip()
        self.link = link

    @staticmethod
    def _get_beautiful_name(name: str):
        words = WORD_PATTERN.findall(name.strip())
        words = list(set(words))
        new_words = [word[0].upper()+word[1:].lower() for word in words]
        for word, new_word in zip(words, new_words):
            name = name.replace(word, new_word)
        return name.strip()

    def _get_pretty_hour(self) -> str:
        if not (self.date.hour == self.date.minute and self.date.minute == 0):
            return self.date.strftime('%H:%M')
        return ""

    def __repr__(self) -> str:
        return f"{self.name} - {self.date.strftime(Event.DATE_DUMP_FORMAT)} - {self.professional.name}"

    def to_dict(self) -> dict:
        return {"name": self.name, "date": self.date.strftime(Event.DATE_DUMP_FORMAT), "address": self.address, "link": self.link}

    def get_address_and_professional(self) -> str:
        return ""

    def to_markdown(self) -> str:
        event_md = f"[{self.name}]({self.link}) organisé par {self.professional.display_name} au {self.address}"
        date = self._get_pretty_hour()
        if date:
            return f"{date} {event_md}"
        return ' '.join(event_md).replace(' ,', ',')

    def to_whatsapp(self) -> str:
        event_md = f"*{self.name}* organisé par *{self.professional.display_name}*"
        date = self._get_pretty_hour()
        if date:
            return f"{date} {event_md}"
        return ' '.join(event_md).replace(' ,', ',')

    def __eq__(self, other: Event):
        return self.name == other.name and self.date == other.date and self.address == other.address and self.professional == other.professional

    @staticmethod
    def _get_even_elem(elem, date_text) -> BeautifulSoup:
        if elem.parent.text == date_text:
            return Event._get_even_elem(elem.parent, date_text)
        return elem.parent

    @staticmethod
    def from_facebook_page(professional: Professional, soup: BeautifulSoup) -> list[Event]:
        if "Upcoming" not in soup.text:
            print(f"No future events found for {professional.display_name}")
            return []
        events = []
        for elem in soup.find_all('span'):
            match = Event.FACEBOOK_DATE_PATTERN.match(elem.text)
            if match:
                date = datetime.strptime(f'{TODAY.year} '+' '.join(match.groups()), '%Y %b %d %I:%M %p')

                event_elem = Event._get_even_elem(elem, elem.text)

                links = event_elem.find_all('a', href=Event.FACEBOOK_LINK_PATTERN)
                link = ""
                if links:
                    link = links[0]['href']

                elem_dict = event_elem.get_text(separator=';').split(";")
                elem_dict.remove(elem.text)

                event = Event(date=date, name=elem_dict[0],
                              address=elem_dict[1], professional=professional, link=link)

                if event not in events:
                    events.append(event)

        return events


class Professional:
    def __init__(self,
                 name: str,
                 relative_url: str,
                 display_name: str = "",
                 email: str = "",
                 phone: str = "",
                 address: str = "",
                 urls: list = [],
                 page_type: str = "",
                 subscribed: bool = False,
                 events: list[Event] = []):
        assert name
        assert relative_url and " " not in relative_url, f"{relative_url} is not a valid relative_url"
        self.name = name.strip()
        if display_name:
            self.display_name = display_name.strip()
        else:
            display_name = name
            if display_name.startswith("La ") or display_name.startswith("Le ") or display_name.startswith("Les "):
                display_name = display_name[0].lower()+display_name[1:]
            elif display_name.startswith("A ") or display_name.startswith("a "):
                display_name = "à" + display_name[1:]
            self.display_name = display_name
        self.relative_url = relative_url
        self.events = [Event(**event, professional=self) for event in events]
        self.email = email.strip()
        self.phone = phone.strip()
        self.address = address.strip()
        self.urls = [url.strip() for url in urls]
        self.page_type = page_type.strip()
        self.subscribed = subscribed

    @property
    def event_url(self):
        if "profile" in self.relative_url:
            return f"{self.base_url}&sk=events"
        elif self.relative_url.startswith("people"):
            profile_id = self.relative_url.split("/")[-1]
            return f"{FACEBOOK_URL}profile.php?id={profile_id}&sk=events"
        else:
            return f"{self.base_url}/events"

    @property
    def base_url(self):
        return f"{FACEBOOK_URL}{self.relative_url}"

    def get_events(self, driver: webdriver.Chrome):
        self.events = Event.from_facebook_page(self, driver.get_soup(self.event_url))

    @staticmethod
    def from_url() -> list[Professional]:
        # Only works for the firsts followers
        # driver.get("https://www.facebook.com/parisbeerclub/following")
        # elem = driver.find_elements(By.XPATH, FOLLOWING_PATH)
        # soup = BeautifulSoup(elem[0].get_attribute('innerHTML'), )
        raise NotImplementedError()

    KEY_DICT_LIST = [
        "name",
        "relative_url",
        "display_name",
        "email",
        "phone",
        "address",
        "urls",
        "page_type",
        "subscribed"
    ]

    def to_dict(self, get_events: bool = False) -> dict[str]:
        my_dict = {key: self.__dict__[key] for key in Professional.KEY_DICT_LIST}
        if get_events:
            my_dict["events"] = [event.to_dict() for event in self.events]
        return my_dict

    PHONE_NUMBER_PATTERN = re.compile(r"\d\d ?\d\d ?\d\d ?\d\d ?\d\d")
    ADDRESS_PATTERN = re.compile(r".*, France")
    EMAIL_PATTERN = re.compile(r"^((?!\.)[\w\-_.]*[^.])(@\w+)(\.\w+(\.\w+)?[^.\W])$")
    URL_PATTERN = re.compile(r"[-a-zA-Z0-9@:%._\+~#=]{1,256}\.[a-zA-Z0-9()]{1,6}\b([-a-zA-Z0-9()@:%_\+.~#?&//=]*)")
    INTRO_KEY = "Intro"
    PAGE_TYPE_KEY = "Page"

    @staticmethod
    def _get_relevant_data(soup: BeautifulSoup) -> dict[str]:
        data = [data.strip() for data in soup.get_text(separator='\n').split('\n') if data.strip()]
        i_start = 0
        for i, data_str in enumerate(data):
            if "Informations de compte oubliées" in data_str:
                name = data[i+1]
            elif data_str == Professional.INTRO_KEY:
                i_start = i
            elif "Confidentialité" in data_str:
                break
        data = data[i_start:i]
        phone = ""
        urls = []
        address = ""
        email = ""
        intro = ""
        professional_type = ""
        for data_str in data:
            if not phone and Professional.PHONE_NUMBER_PATTERN.match(data_str):
                phone = data_str
            elif not address and Professional.ADDRESS_PATTERN.match(data_str):
                address = data_str
            elif not email and Professional.EMAIL_PATTERN.match(data_str):
                email = data_str
            elif Professional.URL_PATTERN.match(data_str):
                urls.append(data_str)
            elif not intro and data_str == Professional.INTRO_KEY:
                intro = Professional.INTRO_KEY
            elif intro == Professional.INTRO_KEY:
                intro = data_str
            elif not professional_type and data_str == Professional.PAGE_TYPE_KEY:
                professional_type = Professional.PAGE_TYPE_KEY
            elif professional_type == Professional.PAGE_TYPE_KEY:
                professional_type = data_str.replace("·", "").strip()
            else:
                # print(f"Ignoring {data_str}")
                pass

        return {
            "name": name,
            "email": email,
            "phone": phone,
            "address": address,
            "urls": urls,
            "page_type": professional_type
        }

    @staticmethod
    def from_relative_url(driver: Driver, relative_url: str) -> Professional:
        base_url = Professional("dummy", relative_url).base_url
        soup = driver.get_soup(base_url+"?locale=fr_FR")
        data = Professional._get_relevant_data(soup)
        data["relative_url"] = relative_url
        return Professional(**data)


class Professionals:
    def __init__(self, all_professionals = True):
        self.professionals_file_path = "data/professionals.json"

        with open(self.professionals_file_path, "r", encoding="utf-8") as file_stream:
            self._professionals = [Professional(**sub) for sub in json.load(file_stream)]
        
        self.all_professionals = all_professionals

        self.events_file_path = "output/professionals.json"

        self.driver = Driver()

        self.build_professionals()

        self.modified_date = None
        if os.path.exists(self.events_file_path):
            self.modified_date = datetime.fromtimestamp(os.path.getmtime(self.events_file_path))
            with open(self.events_file_path, "r", encoding="utf-8") as file_stream:
                temp_pros = {sub["relative_url"]:Professional(**sub) for sub in json.load(file_stream)}
            for pro in self._professionals:
                pro.events = temp_pros[pro.relative_url].events

    def build_professionals(self):
        print("Building professionals...")

        bar = alive_it(self._professionals)
        for professional in bar:
            bar.text(f"{professional.relative_url}")
            if not professional.name:
                professional = Professional.from_relative_url(self.driver, professional.relative_url)
        self.save(self.professionals_file_path, False)

    def get_events(self, force_get_event: bool = False):
        print("Getting events...")
        bar = alive_it(self._professionals)
        for professional in bar:
            if (professional.subscribed or self.all_professionals) and (self.modified_date is None or force_get_event or self.modified_date < TODAY):
                professional.get_events(self.driver)
                bar.text(f"Fetching event for {professional.display_name}")
            else:
                bar.text(f"Loading event from file for {professional.display_name}")

        self.save(self.events_file_path, True)

    def save(self, file_path: str, save_event: bool = False):
        with open(file_path, "w", encoding="utf-8") as file_stream:
            json.dump([sub.to_dict(save_event) for sub in self._professionals], file_stream, indent=4, ensure_ascii=False)

    def __iter__(self):
        return self._professionals.__iter__()

    def __next__(self):
        return self._professionals.__next__()


if __name__ == "__main__":
    subs = Professionals()
    subs.get_events(False)
