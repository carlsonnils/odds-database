import pickle

import httpx
import pyodbc 


def insert_response(
    db_conn: pyodbc.Connection, 
    response: httpx.Response,
) -> int:
    cursor = db_conn.cursor()    
    inserted_row = -1

    try:
        cursor.execute("""
            INSERT INTO responses (endpoint, response) VALUES (?, ?);
        """, response.url.path.split("/")[-1], pickle.dumps(response))
        inserted_row = cursor.rowcount
        db_conn.commit()
    finally:
        cursor.close()

    return inserted_row


def get_latest_response(db_conn: pyodbc.Connection, endpoint: str = ""):
    where_endpoint = ""
    if endpoint != "":
        where_endpoint = f"WHERE endpoint = {endpoint}"
    
    cursor = db_conn.cursor()

    try:
        cursor.execute(f"""
            SELECT * 
            FROM responses
            {where_endpoint}
            ORDER BY time_received DESC
            LIMIT 1
        """)
        row = cursor.fetchone()
    finally:
        cursor.close()

    row[-2] = pickle.loads(row[-2])

    return row
