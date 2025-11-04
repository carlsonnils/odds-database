import os
from datetime import datetime, timedelta

import toml


FILE_NAME = "request_options.toml"


def load_options() -> dict:
    if not os.path.exists(FILE_NAME):
        f = open(FILE_NAME, mode="w")
        f.close()

    options = toml.load(FILE_NAME)

    return options


def write_options(options: dict):
    f = open(FILE_NAME, mode="w")
    toml.dump(options, f)


def check_time_since_trigger(options: dict, time_since: int = 60 * 10) -> bool:
    datetime_format = "%Y-%m-%d %H:%M:%S"

    last_time = options.get("last_request_time", "1900-01-01 00:00:00")
    ts = datetime.today() - datetime.strptime(last_time, datetime_format)

    if ts.total_seconds() > time_since:
        options.update({"last_request_time": datetime.today().strftime(datetime_format)})
        write_options(options)
        return True

    return False


def month_end(dt: datetime) -> datetime:
    d = datetime(dt.year, dt.month, 28)
    d = d + timedelta(days=4)
    d = d - timedelta(days=d.day)
    return d


def check_spaced_trigger(options: dict, usage_multi: int = 1) -> bool:
    datetime_format = "%Y-%m-%d %H:%M:%S"

    last_time = datetime.strptime(
        options.get("last_request_time", "1900-01-01 00:00:00"),
        datetime_format,
    )
    ts = datetime.today() - last_time

    usage = options.get("usage", {})
    remaining = usage.get("remaining", 0)

    if remaining == 0:
        return False

    interval = (month_end(last_time) - last_time).total_seconds() / (remaining * usage_multi) 

    if ts.total_seconds() > interval:
        options.update({"last_request_time": datetime.today().strftime(datetime_format)})
        options.update({"update_interval_sec": interval})
        write_options(options)
        return True

    return False


def update_usage(opts: dict, rem: int, used: int, last: int):
    opts.update({"usage": {
        "remaining": int(rem),
        "used": int(used),
        "last": int(last),
    }})
    write_options(opts)

