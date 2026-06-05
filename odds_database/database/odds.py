import polars as pl
import pyodbc


def upsert_odds(db_conn: pyodbc.Connection, df: pl.DataFrame) -> tuple[int, int]:
    cursor = db_conn.cursor()

    updated_rows = -1
    inserted_rows = -1

    try:
        cursor.execute("DROP TEMPORARY TABLE IF EXISTS odds_temp")

        cursor.execute("CREATE TEMPORARY TABLE odds_temp LIKE odds_test")

        # insert into temp table
        cursor.executemany(f"""
            INSERT INTO odds_temp ({', '.join(df.columns)})
            VALUES ({', '.join(['?'] * len(df.columns))})
            """, df.iter_rows())

        # update changed lines from temp table
        cursor.execute(f"""
            UPDATE odds_test o 
            JOIN odds_temp t 
            ON o.game_id = t.game_id
                AND o.book_key = t.book_key
                AND o.last_update_book = t.last_update_book
                AND o.market_key = t.market_key
                AND o.last_update_market = t.last_update_market
                AND o.team_name = t.team_name
            SET o.price = t.price
        """)
        updated_rows = cursor.rowcount

        # insert new rows from temp table
        cursor.execute(f"""
            INSERT INTO odds_test
            SELECT * 
            FROM odds_temp t 
            WHERE NOT EXISTS (
                SELECT 1 
                FROM odds_test o 
                WHERE o.game_id = t.game_id
                    AND o.book_key = t.book_key
                    AND o.last_update_book = t.last_update_book
                    AND o.market_key = t.market_key
                    AND o.last_update_market = t.last_update_market
                    AND o.team_name = t.team_name 
            )
        """)
        inserted_rows = cursor.rowcount
        db_conn.commit()

        cursor.execute("DROP TEMPORARY TABLE IF EXISTS odds_temp")
        db_conn.commit()

    except Exception as e:
        print(f"Error: {e}")
        db_conn.rollback()

    finally:
        cursor.close()

    return inserted_rows, updated_rows
