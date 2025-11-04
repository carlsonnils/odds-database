import os

import httpx


HOST = "https://api.the-odds-api.com/v4"


def fetch_usage():
    params = {"apiKey": os.environ.get("ODDSAPI_KEY")}

    r = httpx.get(
        HOST + "/sports",
        params=params,
    )

    h = r.headers

    return h.get("x-requests-remaining", 0), h.get("x-requests-used", 0), h.get("x-requests-last")


def fetch_sports(options: dict) -> httpx.Response:
    params = {"apiKey": os.environ.get("ODDSAPI_KEY")}
    params.update(options.get("sports", {}))

    r = httpx.get(
        HOST + "/sports",
        params=params,
    )

    return r


def fetch_odds(options: dict, sport: str = "upcoming") -> httpx.Response:
    params = {"apiKey": os.environ.get("ODDSAPI_KEY")}
    params.update(options.get("odds", {}))

    r = httpx.get(
        HOST + f"/sports/{sport}/odds",
        params=params,
    )

    return r
