import sqlite3
import pandas as pd
import numpy as np

## load test dataset
print("\n\n Load test table...")

db_name = "sample_data/steel.db"
conn = sqlite3.connect(db_name)
c = conn.cursor()
c.execute("SELECT * FROM test")
cols = [col[0] for col in c.description]
dat = pd.DataFrame(data=c.fetchall(),columns=cols)
conn.close()

## make prediction for test set
print("\n\n make prediction...")
pred = inference(dat)

## insert prediction into predict table
print("\n\n insert predict table...")
db_name = "sample_data/steel.db"
conn = sqlite3.connect(db_name)
c = conn.cursor()
c.executemany("INSERT INTO predict VALUES (?)", pred)
conn.commit()

## print predict table
print("\n\n predict table...")
c.execute("SELECT * FROM predict limit 10")
items = c.fetchall()
for item in items:
    print(item)

conn.close()