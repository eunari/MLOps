import sqlite3
import pandas as pd
import requests

def connect_db(db_name):
    """Connect to SQLite database."""
    try:
        conn = sqlite3.connect(db_name)
        return conn
    except Exception as e:
        print(f"Error connecting to the database: {e}")
        return None

def get_random_row(conn, table_name):
    """Fetch a random row from the specified table."""
    try:
        query = f"SELECT * FROM {table_name}"
        df = pd.read_sql_query(query, conn)
        if df.empty:
            raise ValueError("The table is empty.")
        return df.sample(n=1)
    except Exception as e:
        print(f"Error fetching random row: {e}")
        return None

def call_api(api_url, row):
    """Call the prediction API with a row of data."""
    try:
        payload = {"data": [row.to_dict(orient="records")[0]]}
        response = requests.post(api_url, json=payload)
        response.raise_for_status()
        return response.json()
    except Exception as e:
        print(f"Error during API call: {e}")
        return None

def insert_prediction(conn, prediction, table_name="predict"):
    """Insert prediction into the predict table."""
    try:
        c = conn.cursor()
        predict = prediction["prediction"][0]
        c.execute("INSERT INTO predict (predict) VALUES (?)", (str(predict),))
        conn.commit()
    except Exception as e:
        print(f"Error inserting prediction into the database: {e}")
