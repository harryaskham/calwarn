from typing import Callable
import re
import sys
import requests
import icalendar
import pathlib
import csv
from datetime import datetime, timedelta
from urllib.request import urlopen
import argparse

parser = argparse.ArgumentParser(
    description="calwarn - take action based on ics content"
)
parser.add_argument("--ics", help="Path or URL to ICS content")
parser.add_argument("--spec", help="CSV predicate spec. i.e. days=1,location=Emirates Stadium")
parser.add_argument("--tmpl", help="Warning template i.e. \"{{SUMMARY}} at {{LOCATION}}\"")
parser.add_argument("--token", help="Telegram bot token")
parser.add_argument("--chat_id", help="Chat ID to notify")
v_group = parser.add_mutually_exclusive_group()
v_group.add_argument("-v", action="store_true")
v_group.add_argument("-vv", action="store_true")
v_group.add_argument("-vvv", action="store_true")


class Spec:

    def __init__(self, specs: list[Callable[[icalendar.Event], bool]] = []):
        self._specs = specs

    @classmethod
    def from_csv(cls, spec_csv: str):
        specs = []
        for row in csv.reader([spec_csv]):
            for kv in row:
                k, v = kv.split("=")
                match k:
                    case "days":
                        days = int(v)
                        specs.append(
                            lambda e: (
                                e.start.date() >= datetime.today().date()
                                and e.start.date() <= datetime.today().date() + timedelta(days=days)))
                    case "location":
                        location = v
                        specs.append(lambda e: e.get("LOCATION") == location)
                    case _:
                        print(f"Unknown spec: {kv}")
        return cls(specs)

    def match(self, event: icalendar.Event):
        return all(spec(event) for spec in self._specs)


class Template:

    def __init__(self, tmpl: str):
        self._tmpl = tmpl

    def for_event(self, event: icalendar.Event):
        subbed = re.sub(r"{{(.*?)}}", lambda m: event.get(m.group(1)) or event.__dict__.get(m.group(1)), self._tmpl)
        return subbed.format(e=event)


class CalWarn:

    def __init__(self, ics: str, token: str, chat_id: str, spec_csv: str, tmpl: str):
        self._ics = ics
        self._token = token
        self._chat_id = chat_id
        self._spec = Spec.from_csv(spec_csv)
        self._tmpl = Template(tmpl)

    @classmethod
    def from_ics_path(cls, ics_path: str, *args, **kwargs):
        try:
            return cls(pathlib.Path(ics_path).open().read(), *args, **kwargs)
        except Exception:
            print(f"{ics_path} failed to open by path, trying URL")
            return cls(urlopen(ics_path).read(), *args, **kwargs)

    def run(self):
        cal = icalendar.Calendar.from_ical(self._ics)
        events = [e for e in cal.walk("VEVENT") if self._spec.match(e)]
        warnings = [self._tmpl.for_event(e) for e in events]
        message_url = f"https://api.telegram.org/bot{self._token}/sendMessage"
        print(message_url)

        if not warnings:
            print("No matching events")
            return

        # telegram_send.configure
        print(f"Sending warnings for {len(warnings)} matching events")
        for warning in warnings:
            print(f"Sending warning: {warning}")
            params = {"chat_id": self._chat_id, "text": warning}
            resp = requests.get(message_url, params=params).json()
            if resp["ok"]:
                print("Sent warning")
            else:
                print(f"Send error: {resp['error_code']} {resp['description']}")



def init_args():
    try:
        args = parser.parse_args()
    except argparse.ArgumentError as e:
        print(f"Error parsing arguments: {e}")
        return 1
    return args


def main():
    args = init_args()
    calwarn = CalWarn.from_ics_path(
            ics_path=args.ics,
            token=args.token,
            chat_id=int(args.chat_id),
            spec_csv=args.spec,
            tmpl=args.tmpl)
    calwarn.run()


if __name__ == "__main__":
    sys.exit(main())
