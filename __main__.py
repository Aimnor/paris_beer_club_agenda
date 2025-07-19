from datetime import datetime
import sys
from source import BeerAgenda

if __name__ == "__main__":
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
