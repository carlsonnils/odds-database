import httpx


BASE_URL = "https://api.the-odds-api.com/v4"


def extract_usage(headers: httpx.Headers) -> dict:
    return {k: v for k, v in headers.items() if "x-requests" in k}



def fetch_usage(api_key: str) -> dict:
    r = httpx.get(BASE_URL + "/sports", params={"apiKey": api_key})

    if r.status_code != 200:
        print("Error getting Odds API usage: ", r.reason_phrase)

    return extract_usage(r.headers)


def fetch_sports(api_key: str, options: dict) -> httpx.Response:
    params = {"apiKey": api_key}
    params.update(options.get("sports", {}))

    r = httpx.get(BASE_URL + "/sports", params=params)

    if r.status_code != 200:
        print("Error getting Odds API sports: ", r.reason_phrase)

    return r


def fetch_odds(api_key: str, options: dict, sport: str) -> httpx.Response:
    params = {"apiKey": api_key}
    params.update(options.get("odds", {}))

    r = httpx.get(BASE_URL + f"/sports/{sport}/odds", params=params)

    if r.status_code != 200:
        print("Error getting Odds API odds: ", r.reason_phrase)

    return r
