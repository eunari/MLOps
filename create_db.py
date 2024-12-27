import sqlite3
import pandas as pd

db_name = "data/steel.db"
conn = sqlite3.connect(db_name)
c = conn.cursor()

### create train table into DB ###
train = pd.read_csv("data/train.csv")
train.to_sql("train", conn, index=False)

### create test table into DB ###
test = pd.read_csv("data/test.csv")
test.to_sql("test", conn, index=False)

### create predict table ###
c.execute("""CREATE TABLE predict(predict TEXT)""")
conn.commit()


print("\n\n train table...")

c.execute("SELECT * FROM train")
items = c.fetchall()
for item in items:
    print(item)

print("\n\n test table...")    
    
c.execute("SELECT * FROM test")
items = c.fetchall()
for item in items:
    print(item)
    
print("\n\n predict table...")

c.execute("SELECT * FROM predict")
items = c.fetchall()
for item in items:
    print(item)

    
## close our connection
conn.close()
