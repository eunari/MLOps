import sqlite3
import pandas as pd
import numpy as np
import pickle as pkl

db_name = "data/steel.db"
conn = sqlite3.connect(db_name)
c = conn.cursor()
c.execute("SELECT * FROM train")
cols = [col[0] for col in c.description]
dat = pd.DataFrame(data=c.fetchall(),columns=cols)
conn.close()

## train, test split
from sklearn.model_selection import train_test_split
train, test = train_test_split(dat, test_size=0.3)
train.head()

## x variables preprocessing 
x_cols = ['V'+str(i) for i in range(1,28)]
from sklearn.preprocessing import StandardScaler
trans = StandardScaler()
trans.fit(train[x_cols])
train_x = trans.transform(train[x_cols])

## y variables preprocessing
train['V34'] = train['Class']-1
train_y = [str(np.where(r==1)[0][0]) for r in train[['V'+str(i) for i in range(28,35)]].to_numpy()]

## classification modeling 
from sklearn.ensemble import RandomForestClassifier
model = RandomForestClassifier()
model.fit(train_x, train_y)

## save model and transformation 
print("creating model file...")
pkl.dump(model, open("Model.pkl","wb"))
print("creating transformation file...")
pkl.dump(trans, open("Trans.pkl","wb"))

## make prediction for testset
test_x = trans.transform(test[x_cols])
pred = model.predict(test_x)

## validation for testset
test['V34'] = test['Class']-1
test_y = [str(np.where(r==1)[0][0]) for r in test[['V'+str(i) for i in range(28,35)]].to_numpy()]
print(np.mean(pred==test_y))
print(pd.crosstab(test_y, pred))
