import polars as pl
import httpx


def df_from_sports_response(response: httpx.Response) -> pl.DataFrame:
    df = pl.from_dicts(response.json())
    return df.rename({
        "key": "sport_key",
        "group": "sport_type",
        "title": "league",
        "active": "in_season",
    })


def df_from_odds_response(response: httpx.Response) -> pl.DataFrame:
    df = (
        pl.from_dicts(response.json())
        .explode("bookmakers")
        .unnest("bookmakers")
        .rename(
            {
                "key": "book_key", 
                "last_update": "last_update_book",
                "link": "book_link",
                "sid": "book_sid",
            }
        )
        .explode("markets")
        .unnest("markets")
        .explode("outcomes")
        .rename({"link": "outcome_link", "sid": "outcome_sid"})
        .unnest("outcomes")
        .rename(
            {
                "id": "game_id",
                "title": "book_title",
                "key": "market_key",
                "last_update": "last_update_market",
                "name": "team_name",
            }
        ).with_columns(
            pl.col("commence_time").str.to_datetime("%Y-%m-%dT%H:%M:%SZ"),
            pl.col("last_update_book").str.to_datetime("%Y-%m-%dT%H:%M:%SZ"),
            pl.col("last_update_market").str.to_datetime("%Y-%m-%dT%H:%M:%SZ"),
        )
    )

    return df
