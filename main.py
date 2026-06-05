from datetime import datetime, timedelta
import os
import sys
import time

from dotenv import load_dotenv
import pyodbc

from odds_database import (
    config,
    odds_api,
    database,
)
from odds_database.logger import logger


def eomonth(dt: datetime) -> datetime:
    d = datetime(dt.year, dt.month, 28)
    d = d + timedelta(days=4)
    d = d - timedelta(days=d.day)
    return d


def check_trigger(usage: dict[str, str], last_response_time: datetime) -> bool:
    # time until month ends
    current_time = datetime.now()
    time_left = eomonth(current_time) - current_time

    # time between requests (seconds)
    requests_remaining = int(usage.get("x-requests-remaining", "0"))
    if requests_remaining == 0:
        return False

    time_between_requests = int(time_left.total_seconds() / requests_remaining)
    logger.info(f"Time between requests: {timedelta(seconds=time_between_requests)}")

    # time since last request (seconds)
    time_since_latest = (datetime.now() - last_response_time).total_seconds()

    if time_since_latest < time_between_requests:
        logger.info(f"No update triggered. Waiting {timedelta(seconds=time_between_requests - time_since_latest)}")
    
    return time_since_latest >= time_between_requests


def update_database(odds_api_key: str, cfg: dict, db_conn: pyodbc.Connection):
    # get sports
    sports_res = odds_api.fetch_sports(odds_api_key, cfg)
    # save response to database
    num_rows = database.insert_response(db_conn, sports_res)
    # get sports dataframe
    sports_df = odds_api.df_from_sports_response(sports_res)
    # upsert sports table
    inserted_rows, updated_rows = database.upsert_sports(db_conn, sports_df)
    logger.info(f"sports table: inserted {inserted_rows}, updated {updated_rows}")

    # get odds
    odds_res = odds_api.fetch_odds(odds_api_key, cfg, "upcoming")
    # save response to database
    num_rows = database.insert_response(db_conn, odds_res)
    # get odds dataframe
    odds_df = odds_api.df_from_odds_response(odds_res)
    # upsert odds table
    inserted_rows, updated_rows = database.upsert_odds(db_conn, odds_df)
    logger.info(f"odds table: inserted {inserted_rows}, updated {updated_rows}")


def main():
    while True:
        # load environment variables
        load_dotenv()

        # create database connection
        db_conn = pyodbc.connect(os.environ.get("ODDS_DATABASE_CONNSTR", ""))
        if db_conn == "":
            sys.exit("Error: Database connection string not set")
        
        # load Odds API request config
        cfg = config.load_config("request_options.toml")

        # check api usage
        odds_api_key = os.environ.get("ODDS_API_KEY", "")
        if odds_api_key == "":
            sys.exit("Error: Odds API Key not set")

        # check if should get odds data
        usage = odds_api.fetch_usage(odds_api_key)
        last_response_time = database.get_latest_response(db_conn)[-1]
        if check_trigger(usage, last_response_time):
            update_database(odds_api_key, cfg, db_conn)

        # check api usage
        usage = odds_api.fetch_usage(odds_api_key)
        logger.info(f"OddsAPI useage: {usage}")

        # wait before checking again
        wait_seconds = 120
        logger.info(f"Running again in {timedelta(seconds=wait_seconds)}\n")
        time.sleep(wait_seconds)


if __name__ == "__main__":
    main()
