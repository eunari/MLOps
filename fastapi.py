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
    data: List

app = FastAPI()

@app.post("/predict")
def get_prediction(dat: Dataset):
    data = dict(dat)["data"][0]
    data = pd.DataFrame(data=[data.values()], columns=data.keys())
    trans_x = trans.transform(data)
    prediction = model.predict(trans_x).tolist()
    log_proba = model.predict_proba(trans_x).tolist()
    result = {"prediction": prediction, "log_proba": log_proba}
    return result


if __name__ == "__main__":
    print("test")
