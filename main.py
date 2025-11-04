import time

from dotenv import load_dotenv

import options as o
import odds_api as oa
import odds_data as od
import server_db as sdb


load_dotenv()


"""
app loop flow:
    1. open and read the options file (request_options.toml)
    2. check last request datetime,  if it exists read it and calculate whether to trigger, create it if it doesn't and triggers the request
    3. if triggered get upcoming odds data
    4. flatten and format data
    5. write odds data to database
"""


MIN_WAIT_TIME = 1


def update_usage(options):
    remaining, used, last = oa.fetch_usage()
    o.update_usage(options, remaining, used, last)


def update_sports(options: dict):
    r = oa.fetch_sports(options)
    df = od.df_from_sports(r)
    ir, ur = sdb.upsert_sports(df)
    print(f"sports: inserted {ir} rows, updated {ur} rows")


def update_odds(options: dict):
    r = oa.fetch_odds(options)
    df = od.flat_df_from_odds(r)
    ir, ur = sdb.upsert_odds(df)
    print(f"sports: inserted {ir} rows, updated {ur} rows")


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

        update_usage(options)

        time.sleep(MIN_WAIT_TIME)


if __name__ == "__main__":
    main()
