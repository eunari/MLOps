import sqlite3
import pandas as pd
import requests
import random

# Step 1: Connect to SQLite database
db_name = "steel.db"
conn = sqlite3.connect(db_name)
c = conn.cursor()

# Step 2: Check if 'test' table exists and select a random row
try:
    test_df = pd.read_sql_query("SELECT * FROM test", conn)
    if test_df.empty:
        print("The test table is empty.")
        conn.close()
        exit()
    else:
        # Randomly select one row
        random_row = test_df.sample(n=1).to_dict(orient="records")[0]
        print("Random row selected from test table:", random_row)
except Exception as e:
    print(f"Error accessing test table: {e}")
    conn.close()
    exit()

# Step 3: Call FastAPI Web-API for prediction
api_url = "https://curly-parakeet-7v57wg9vxrw6crv95-8000.app.github.dev/predict"  # Replace with your actual FastAPI endpoint

try:
    response = requests.post(api_url, json=random_row)
    if response.status_code == 200:
        prediction = response.json().get("prediction")
        print("Prediction received from API:", prediction)
    else:
        print(f"API call failed with status code {response.status_code}: {response.text}")
        conn.close()
        exit()
except Exception as e:
    print(f"Error calling the API: {e}")
    conn.close()
    exit()

# Step 4: Insert prediction into the predict table
try:
    # Ensure the predict table exists
    c.execute("""
        CREATE TABLE IF NOT EXISTS predict (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            predict TEXT
        )
    """)

    # Insert prediction into the table
    c.execute("INSERT INTO predict (predict) VALUES (?)", (str(prediction),))
    conn.commit()
    print("Prediction successfully inserted into the predict table.")
except Exception as e:
    print(f"Error inserting prediction into the database: {e}")
finally:
    conn.close()
