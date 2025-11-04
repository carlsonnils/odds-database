import os

import polars as pl
import pyodbc


def upsert_odds(df: pl.DataFrame):
    drop_temp = "DROP TEMPORARY TABLE IF EXISTS temp_odds"

    create_temp = "CREATE TEMPORARY TABLE temp_odds LIKE odds"

    insert_into_temp = """
    INSERT INTO temp_odds (game_id, sport_key, sport_title, commence_time, home_team, away_team, book_key, book_title, last_update_book, market_key, last_update_market, team_name, price)
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
    """

    update_with_temp = """
    UPDATE odds o
    JOIN temp_odds t ON o.game_id = t.game_id 
        AND o.sport_key = t.sport_key 
        AND o.book_key = t.book_key 
        AND o.market_key = t.market_key 
        AND o.team_name = t.team_name
    SET o.last_update_book = t.last_update_book,
        o.last_update_market = t.last_update_market,
        o.price = t.price
    """

    insert_new = """
    INSERT INTO odds
    SELECT * FROM temp_odds t
    WHERE NOT EXISTS (
        SELECT 1 FROM odds o
        WHERE o.game_id = t.game_id 
        AND o.sport_key = t.sport_key 
        AND o.book_key = t.book_key 
        AND o.market_key = t.market_key 
        AND o.team_name = t.team_name
    )
    """

    conn = pyodbc.connect(os.environ.get("DATABASE_CONNSTR", ""))
    cursor = conn.cursor()

    try:
        cursor.execute(drop_temp)
        cursor.execute(create_temp)

        cursor.executemany(insert_into_temp, df.iter_rows())

        cursor.execute(update_with_temp)
        updated_rows = cursor.rowcount

        cursor.execute(insert_new)
        inserted_rows = cursor.rowcount
        conn.commit()

    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()

    finally:
        cursor.close()
        conn.close()

    return updated_rows, inserted_rows


def upsert_sports(df: pl.DataFrame):
    drop_temp = """
    DROP TEMPORARY TABLE IF EXISTS temp_sports
    """

    create_temp = """
    CREATE TEMPORARY TABLE temp_sports LIKE sports
    """

    insert_into_temp = """
    INSERT INTO temp_sports (sport_key, sport_type, league, description, in_season, has_outrights)
    VALUES (?, ?, ?, ?, ?, ?)
    """

    update_with_temp = """
    UPDATE sports s
    JOIN temp_sports t ON s.sport_key = t.sport_key
    SET s.in_season = t.in_season,
        s.has_outrights = t.has_outrights
    """

    insert_new = """
    INSERT INTO sports
    SELECT * FROM temp_sports t
    WHERE NOT EXISTS (
        SELECT 1 FROM sports s
        WHERE s.sport_key = t.sport_key
    )
    """

    conn = pyodbc.connect(os.environ.get("DATABASE_CONNSTR", ""))
    cursor = conn.cursor()

    try:
        cursor.execute(drop_temp)
        cursor.execute(create_temp)

        cursor.executemany(insert_into_temp, df.iter_rows())

        cursor.execute(update_with_temp)
        updated_rows = cursor.rowcount

        cursor.execute(insert_new)
        inserted_rows = cursor.rowcount

        conn.commit()

    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()

    finally:
        cursor.close()
        conn.close()

    return inserted_rows, updated_rows
