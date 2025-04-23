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
    def __init__(self, force_get_event: bool = False):
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

    def _dumps_beer_agenda(self, beer_agenda_file_path):
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
    if len(sys.argv) not in [1, 3]:
        print("Usage: `python main.py` or `python main.py start_date stop_date`")
        sys.exit(1)
    if len(sys.argv) == 3:
        start = datetime.strptime(sys.argv[1], "%Y_%m_%d")
        stop = datetime.strptime(sys.argv[2], "%Y_%m_%d")
    ba = BeerAgenda()
    if len(sys.argv) == 1:
        ba.create_beer_agenda()
    else:
        ba.create_beer_agenda(start, stop)
