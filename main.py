import os
import pickle
import pandas as pd
from pydantic import BaseModel, conlist
from typing import List
from fastapi import FastAPI, Body

with open("Model.pkl", "rb") as f:
    model = pickle.load(f)

with open("Trans.pkl","rb") as f:
    trans = pickle.load(f)

class Dataset(BaseModel):
    data: List[dict]

app = FastAPI()

@app.post("/predict")
def get_prediction(dat: Dataset):
    data = dict(dat)["data"][0]
    data_df = pd.DataFrame([data])

    trans_x = trans.transform(data_df)
    prediction = model.predict(trans_x).tolist()
    log_proba = model.predict_proba(trans_x).tolist()

    result = {"prediction": prediction, "log_proba": log_proba}
    return result


if __name__ == "__main__":
    print("test")
