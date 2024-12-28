import dash
from dash.dependencies import Input, Output, State
import plotly.express as px
import plotly.graph_objects as go

import app_layout as al
import mylib as my
from online_infer_function import connect_db, get_random_row, call_api, insert_prediction

import pandas as pd
import numpy as np
import sys, os
import datetime
import pickle as pkl

import requests

DB_NAME = "data/steel.db"
API_URL = "https://curly-parakeet-7v57wg9vxrw6crv95-8000.app.github.dev/predict"

items = ['button1','time1', 'pred1', 'graph1', 'table1']

app = dash.Dash()
app.layout = al.app_layout(items)

@app.callback(
    Output('time1','children'),
    Output('table1','data'),
    Output('pred1', 'children'),
    Output('graph1', 'figure'),
    Input('button1','n_clicks'),
    prevent_initial_call=False)

def fn(n_clicks):
    # Current time
    current_time = str(datetime.datetime.now())

    # Connect to the database
    conn = connect_db(DB_NAME)
    if not conn:
        return current_time, [], "Database connection failed", px.line()

    # Fetch a random row
    print("[INFO] Fetching a random row from the 'test' table...")
    random_row = get_random_row(conn, table_name="test")
    if random_row is None:
        print("[ERROR] Failed to fetch random row from the 'test' table.")
        conn.close()
        return current_time, [], "Failed to fetch random row", px.line()

    print(f"[INFO] Random row fetched: {random_row.to_dict('records')}")

    # Call the prediction API
    print("[INFO] Calling the prediction API...")
    prediction = call_api(API_URL, random_row)
    print("prediction ::::" , prediction)
    predict = prediction["prediction"][0]
    if prediction is None:
        print("[ERROR] API call failed.")
        conn.close()
        return current_time, [], "API call failed", px.line()

    print(f"[INFO] Prediction received: {prediction}")

    # Save the prediction into the database
    print("[INFO] Inserting prediction into the 'predict' table...")
    try:
        # Using insert_prediction from online_infer
        insert_prediction(conn, prediction, table_name="predict")
        my.df_to_db(random_row, DB_NAME, "input_x")
    except Exception as e:
        print(f"[ERROR] Failed to insert prediction into the database: {e}")
        conn.close()
        return current_time, [], "Failed to save prediction", px.line()

    # Generate output
    print("[INFO] Generating output...")
    try:
        pred_history = my.db_to_df(DB_NAME, "predict")  # pred 테이블의 데이터 가져오기
        print(pred_history.head())
        pred_history["predict"] = pd.to_numeric(pred_history["predict"], errors="coerce")
        print(pred_history.head())
        print(pred_history.dtypes)
        fig = px.line(
            x=pred_history.index,
            y=pred_history["predict"].tolist(),
            labels={"x": "Index", "y": "Prediction"}, 
            title="Prediction History"
        )

        # 입력값 테이블 생성
        input_history = my.db_to_df(DB_NAME, "input_x")
        table_data = input_history.to_dict("records")   
    except Exception as e:
        print(f"[ERROR] Failed to generate graph: {e}")
        fig = px.line()
        table_data = []

    

    conn.close()

    print("[INFO] Processing completed successfully.")
    return current_time, table_data, predict, fig

app.run_server()
