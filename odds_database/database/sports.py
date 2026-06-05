import polars as pl
import pyodbc


def upsert_sports(db_conn: pyodbc.Connection, df: pl.DataFrame) -> tuple[int, int]:
    cursor = db_conn.cursor()

    updated_rows = -1
    inserted_rows = -1

    try:
        cursor.execute("DROP TEMPORARY TABLE IF EXISTS sports_temp")

        cursor.execute("CREATE TEMPORARY TABLE sports_temp LIKE sports")

        # insert into temp table
        cursor.executemany(f"""
            INSERT INTO sports_temp ({', '.join(df.columns)})
            VALUES ({', '.join(['?'] * len(df.columns))})
            """, df.iter_rows())

        # update changed lines from temp table
        cursor.execute(f"""
            UPDATE sports s 
            JOIN sports_temp t 
            ON s.sport_key = t.sport_key
            SET s.in_season = t.in_season,
                s.has_outrights = t.has_outrights
        """)
        updated_rows = cursor.rowcount

        # insert new rows from temp table
        cursor.execute(f"""
            INSERT INTO sports
            SELECT * 
            FROM sports_temp t 
            WHERE NOT EXISTS (
                SELECT 1 
                FROM sports s 
                WHERE s.sport_key = t.sport_key
            )
        """)
        inserted_rows = cursor.rowcount
        db_conn.commit()

        cursor.execute("DROP TEMPORARY TABLE IF EXISTS sports_temp")
        db_conn.commit()

    except Exception as e:
        print(f"Error: {e}")
        db_conn.rollback()

    finally:
        cursor.close()

    return inserted_rows, updated_rows
