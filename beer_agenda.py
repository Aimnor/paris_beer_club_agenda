from __future__ import annotations

import json
from datetime import timedelta, datetime
from collections import OrderedDict

from professionals import Professionals, TODAY

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
    def __init__(self, force_get_event: bool = False, all_professionals:bool = True):
        self.all_professionals = all_professionals
        self.professionals = Professionals(all_professionals)
        # if all_professionals: TODO
        self.professionals.get_events(force_get_event)

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
        for professional in self.professionals:
            if not professional.events or not professional.subscribed and not self.all_professionals:
                continue
            for event in professional.events:
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

    def _dumps_all_events(self, professionals_file_path):
        with open(professionals_file_path, "w", encoding="utf-8") as file_stream:
            json.dump({professional.name: professional.events_to_dict()
                      for professional in self.professionals}, file_stream, indent=4, ensure_ascii=False)


if __name__ == "__main__":
    import sys
    argv_len = len(sys.argv)
    if argv_len not in [1, 3, 4]:
        print("Usage: `python main.py` or `python main.py start_date stop_date` or `python main.py start_date stop_date mode`")
        sys.exit(1)
    if argv_len >= 3:
        start = datetime.strptime(sys.argv[1], "%Y_%m_%d")
        stop = datetime.strptime(sys.argv[2], "%Y_%m_%d")
    all_professionals = False
    if argv_len >= 4:
        if sys.argv[3] == "full":
            all_professionals = True
            
    ba = BeerAgenda(force_get_event=False, all_professionals=all_professionals)
    if len(sys.argv) == 1:
        ba.create_beer_agenda()
    else:
        ba.create_beer_agenda(start, stop)
