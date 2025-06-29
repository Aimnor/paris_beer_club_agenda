from __future__ import annotations

import json
from datetime import timedelta, datetime
from collections import OrderedDict

from subscriber import Subscribers, TODAY

class BeerAgenda:
    FRENCH_MONTHS = [
        "Janvier",
        "Février",
        "Mars",
        "Avril",
        "Mai",
        "Juin",
        "Juillet",
        "Août",
        "Septembre",
        "Octobre",
        "Novembre",
        "Décembre"
    ]

    FRENCH_DAYS = [
        "Lundi",
        "Mardi",
        "Mercredi",
        "Jeudi",
        "Vendredi",
        "Samedi",
        "Dimanche"
    ]
    def __init__(self, force_get_event: bool = False, all_time_subscribers:bool = False):
        if all_time_subscribers:
            relative_paths_file = "data/all_time_subscribers.txt"
            subscribers_file_path = "data/all_time_subscribers.json"
            self.subscribers = Subscribers(relative_paths_file=relative_paths_file, subscribers_file_path=subscribers_file_path)
        else:
            self.subscribers = Subscribers()
        self.subscribers.get_events(force_get_event)

    @staticmethod
    def _date_to_str(date: datetime):
        return f"{BeerAgenda.FRENCH_DAYS[date.weekday()]} {date.day} {BeerAgenda.FRENCH_MONTHS[date.month-1]}"

    def _prepare_dates(self, start: datetime = TODAY, stop: datetime = None):
        if start is not None and stop is not None:
            assert stop >= start
        elif start is None:
            start = TODAY
            assert stop is None

        if stop is None:
            days_ahead = 6 - start.weekday()
            stop = start + timedelta(days_ahead)

        self.start = start.replace(hour=0, minute=0)
        self.stop = stop.replace(hour=23, minute=59)

        dates = [start + timedelta(days=x) for x in range((stop-start).days + 1)]
        self.dates = OrderedDict()
        for date in dates:
            self.dates[BeerAgenda._date_to_str(date)] = []

    def create_beer_agenda(
            self, start: datetime | None = TODAY, stop: datetime | None = None,
            beer_agenda_file_path: str = "output/beer_agenda.md"):
        self._prepare_dates(start, stop)
        for subscriber in self.subscribers:
            if not subscriber.events:
                continue
            for event in subscriber.events:
                if event.date <= self.stop and event.date >= self.start:
                    self.dates[BeerAgenda._date_to_str(event.date)].append(event)
        self._dumps_beer_agenda(beer_agenda_file_path)

    def _dumps_beer_agenda(self, beer_agenda_file_path, type: str = "whatsapp"):
        if type == "whatsapp":
            beer_agenda_txt = '\n\n'.join([f"*{str_date}*\n"+"\n".join([f"- {event.to_whatsapp()}" for event in sorted(events, key=lambda x: x.date)])
                                           for str_date, events in self.dates.items()])
        elif type == "markdown":
            beer_agenda_txt = '\n\n'.join([f"# {str_date}\n"+"\n".join([f"- {event.to_markdown()}" for event in sorted(events, key=lambda x: x.date)])
                                           for str_date, events in self.dates.items()])
        with open(beer_agenda_file_path, "w", encoding="utf-8") as file_stream:
            file_stream.write(beer_agenda_txt)

    def _dumps_all_events(self, subscribers_file_path):
        with open(subscribers_file_path, "w", encoding="utf-8") as file_stream:
            json.dump({subscriber.name: subscriber.events_to_dict()
                      for subscriber in self.subscribers}, file_stream, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    import sys
    argv_len = len(sys.argv)
    if argv_len not in [1, 3, 4]:
        print("Usage: `python main.py` or `python main.py start_date stop_date` or `python main.py start_date stop_date mode`")
        sys.exit(1)
    if argv_len >= 3:
        start = datetime.strptime(sys.argv[1], "%Y_%m_%d")
        stop = datetime.strptime(sys.argv[2], "%Y_%m_%d")
    all_time_subscribers = False
    if argv_len >= 4:
        if sys.argv[3] == "full":
            all_time_subscribers = True
            
    ba = BeerAgenda(force_get_event=True, all_time_subscribers=all_time_subscribers)
    if len(sys.argv) == 1:
        ba.create_beer_agenda()
    else:
        ba.create_beer_agenda(start, stop)
