import sqlite3
import pandas as pd
import requests
import random

# Step 1: Connect to SQLite database
db_name = "data/steel.db"
conn = sqlite3.connect(db_name)
c = conn.cursor()

# Step 2: Check if 'test' table exists and select a random row
try:
    test_df = pd.read_sql_query("SELECT * FROM test", conn)
    if test_df.empty:
        print("The test table is empty.")
        exit()

    # Randomly select one row
    random_row = test_df.sample(n=1).to_dict(orient="records")[0]
    print("Random row selected from test table:", random_row)

    # Validate required columns
    required_columns = [f"V{i}" for i in range(1, 28)]  # Example required columns
    if not set(required_columns).issubset(random_row.keys()):
        missing_cols = set(required_columns) - set(random_row.keys())
        print(f"Missing required columns in the selected row: {missing_cols}")
        exit()
except Exception as e:
    print(f"Error accessing or validating the 'test' table: {e}")
    conn.close()
    exit()

# Step 3: Call FastAPI Web-API for prediction
api_url = "https://curly-parakeet-7v57wg9vxrw6crv95-8000.app.github.dev/predict"  # Replace with your actual FastAPI endpoint

try:
    payload = {"data": [random_row]}
    print("Payload sent to API:", payload)

    response = requests.post(api_url, json=payload)
    response.raise_for_status()  # Raise an exception for HTTP errors
    prediction = response.json().get("prediction")
    print("Prediction received from API:", prediction)
except requests.exceptions.RequestException as e:
    print(f"Error during API call: {e}")
    conn.close()
    exit()
except Exception as e:
    print(f"Unexpected error during API call: {e}")
    conn.close()
    exit()

# Step 4: Insert prediction into the predict table
try:
    input_data = str(random_row)  # Convert the row to a string for storage
    c.execute("INSERT INTO predict (predict) VALUES (?)", (str(prediction),))
    conn.commit()
    print("Prediction successfully inserted into the predict table.")
except Exception as e:
    print(f"Error inserting prediction into the database: {e}")
finally:
    conn.close()
