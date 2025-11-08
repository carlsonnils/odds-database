import time
import logging

from dotenv import load_dotenv

import options as o
import odds_api as oa
import odds_data as od
import server_db as sdb


load_dotenv()


logger = logging.getLogger("odb")
logger.setLevel(logging.INFO)

formatter = logging.Formatter(
    fmt="{asctime} - {name} - {levelname} - {message}",
    style="{",
)

fh = logging.FileHandler("log.log")
fh.setLevel(logging.INFO)
fh.setFormatter(formatter)
logger.addHandler(fh)

ch = logging.StreamHandler()
ch.setLevel(logging.INFO)
ch.setFormatter(formatter)
logger.addHandler(ch)


MIN_WAIT_TIME = 600


def update_usage(options):
    remaining, used, last = oa.fetch_usage()
    o.update_usage(options, remaining, used, last)


def update_sports(options: dict):
    r = oa.fetch_sports(options)
    df = od.df_from_sports(r)
    ir, ur = sdb.upsert_sports(df)
    logger.info(f"sports: inserted {ir} rows, updated {ur} rows")


def update_odds(options: dict):
    r = oa.fetch_odds(options)
    df = od.flat_df_from_odds(r)
    ir, ur = sdb.upsert_odds(df)
    logger.info(f"odds: inserted {ir} rows, updated {ur} rows")


def main():
    while True:
        options = o.load_options()
        update_usage(options)
        trigger = o.check_spaced_trigger(options)

        if trigger:
            update_odds(options)
            update_sports(options)
            # update_events()
            # update_scores()
            o.print_next_trigger(options)

        update_usage(options)
        time.sleep(MIN_WAIT_TIME)


if __name__ == "__main__":
    main()
