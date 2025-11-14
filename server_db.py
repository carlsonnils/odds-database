import os

import polars as pl
import pyodbc


def upsert_table(
    df: pl.DataFrame, table_name: str, on: list[str], set_vals: None | list[str] = None
):
    # TODO: make sure the on columns are in the df columns
    if set_vals is None:
        set_vals = [x for x in df.columns if x not in on]

    temp_name = f"{table_name}_temp"

    drop_temp = f"DROP TEMPORARY TABLE IF EXISTS {temp_name}"

    create_temp = f"CREATE TEMPORARY TABLE {temp_name} LIKE {table_name}"

    insert_into_temp = (
        f"INSERT INTO {temp_name} ({', '.join(df.columns)}) "
        f"VALUES ({', '.join(['?'] * len(df.columns))})"
    )

    update_with_temp = (
        f"UPDATE {table_name} o "
        f"JOIN {temp_name} t ON {' AND '.join([f'o.{x} = t.{x}' for x in on])} "
        f"SET {' AND '.join([f'o.{x} = t.{x}' for x in set_vals])}"
    )

    insert_new = (
        f"INSERT INTO {table_name} "
        f"SELECT * FROM {temp_name} t "
        f"WHERE NOT EXISTS ( SELECT 1 FROM {table_name} o "
        f"WHERE {' AND '.join([f'o.{x} = t.{x}' for x in on])} )"
    )

    conn = pyodbc.connect(os.environ.get("DATABASE_CONNSTR", ""))
    cursor = conn.cursor()

    updated_rows = -1
    inserted_rows = -1

    try:
        cursor.execute(drop_temp)
        cursor.execute(create_temp)

        cursor.executemany(insert_into_temp, df.iter_rows())

        cursor.execute(update_with_temp)
        updated_rows = cursor.rowcount

        cursor.execute(insert_new)
        inserted_rows = cursor.rowcount
        conn.commit()

        cursor.execute(drop_temp)
        conn.commit()

    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()

    finally:
        cursor.close()
        conn.close()

    return inserted_rows, updated_rows


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
        AND o.last_update_book = t.last_update_book
        AND o.market_key = t.market_key 
        AND o.last_update_market = t.last_update_market
        AND o.team_name = t.team_name
    SET o.price = t.price
    """

    insert_new = """
    INSERT INTO odds
    SELECT * FROM temp_odds t
    WHERE NOT EXISTS (
        SELECT 1 FROM odds o
        WHERE o.game_id = t.game_id 
        AND o.sport_key = t.sport_key 
        AND o.book_key = t.book_key 
        AND o.last_update_book = t.last_update_book
        AND o.market_key = t.market_key 
        AND o.last_update_market = t.last_update_market
        AND o.team_name = t.team_name
    )
    """

    conn = pyodbc.connect(os.environ.get("DATABASE_CONNSTR", ""))
    cursor = conn.cursor()

    updated_rows = -1
    inserted_rows = -1

    try:
        cursor.execute(drop_temp)
        cursor.execute(create_temp)

        cursor.executemany(insert_into_temp, df.iter_rows())

        cursor.execute(update_with_temp)
        updated_rows = cursor.rowcount

        cursor.execute(insert_new)
        inserted_rows = cursor.rowcount
        conn.commit()

        cursor.execute(drop_temp)
        conn.commit()

    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()

    finally:
        cursor.close()
        conn.close()

    return inserted_rows, updated_rows


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

    updated_rows = -1
    inserted_rows = -1

    try:
        cursor.execute(drop_temp)
        cursor.execute(create_temp)

        cursor.executemany(insert_into_temp, df.iter_rows())

        cursor.execute(update_with_temp)
        updated_rows = cursor.rowcount

        cursor.execute(insert_new)
        inserted_rows = cursor.rowcount
        conn.commit()

        cursor.execute(drop_temp)
        conn.commit()

    except Exception as e:
        print(f"Error: {e}")
        conn.rollback()

    finally:
        cursor.close()
        conn.close()

    return inserted_rows, updated_rows
