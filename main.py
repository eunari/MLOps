import os
import pickle
import pandas as pd
from pydantic import BaseModel
from typing import List
from fastapi import FastAPI, HTTPException

# Load model and transformer
with open("Model.pkl", "rb") as f:
    model = pickle.load(f)

with open("Trans.pkl", "rb") as f:
    trans = pickle.load(f)

# Define input data model
class Dataset(BaseModel):
    data: List[dict]

# Initialize FastAPI app
app = FastAPI()

@app.post("/predict")
def get_prediction(dat: Dataset):
    try:
        # Convert input data to DataFrame
        data = dict(dat)["data"]  # Access the 'data' list
        if not data:
            raise ValueError("Input data is empty.")
        
        data_df = pd.DataFrame(data)
        
        # Validate if all required columns are present
        required_columns = [f"V{i}" for i in range(1, 28)]  # Example required columns
        if not set(required_columns).issubset(data_df.columns):
            missing_cols = set(required_columns) - set(data_df.columns)
            raise ValueError(f"Missing required columns: {missing_cols}")
        
        # Apply transformation and make predictions
        trans_x = trans.transform(data_df[required_columns])  # Select required columns
        prediction = model.predict(trans_x).tolist()
        log_proba = model.predict_proba(trans_x).tolist()

        # Return the results
        result = {"prediction": prediction, "log_proba": log_proba}
        return result
    except ValueError as ve:
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        # Log the exception for debugging
        print(f"Error during prediction: {e}")
        raise HTTPException(status_code=500, detail=f"Internal Server Error: {str(e)}")
