import sqlite3
from sqlite3 import Error
import pandas as pd
import numpy as np
from datetime import datetime
import time
import glob

from sklearn.impute import SimpleImputer, KNNImputer
from sklearn.preprocessing import OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestRegressor

import pickle as pk
import requests


def db_to_df_random(db_name, table_name):
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    query = cur.execute("SELECT count(*) FROM " + table_name)
    cnt = query.fetchall()[0][0]
    rid = str(np.random.randint(0,cnt,1)[0])
    query = "SELECT * From " + table_name + " where rowid=" + rid
    out = cur.execute( query )    
    cols = [column[0] for column in out.description]
    result = pd.DataFrame.from_records(data=out.fetchall(), columns=cols)
    con.close()
    return result



def drop_table(db_name, table_name):
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    query = cur.execute( "DROP TABLE " + table_name)    
    con.close()

def db_to_df(db_name, table_name):
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    query = cur.execute( "SELECT * From " + table_name  )    
    cols = [column[0] for column in query.description]
    result = pd.DataFrame.from_records(data=query.fetchall(), columns=cols)
    con.close()
    return result


def db_to_df_rescent(db_name, table_name, time_col, period):
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    query = cur.execute( "SELECT * From " + table_name + " where " + time_col + " <= '" +  str(pd.to_datetime(datetime.now())) + "' AND "+time_col+" >= '" + str(pd.to_datetime(datetime.now()) - pd.to_timedelta(period)) + "'"  )
    cols = [column[0] for column in query.description]
    result = pd.DataFrame.from_records(data=query.fetchall(), columns=cols)
    con.close()
    return result




def df_to_db(df_name, db_name, table_name):
    con = sqlite3.connect(db_name)
    df_name.to_sql(table_name, con,  if_exists='append', index=False)    
    con.close()

    

def df_to_db_col_only(df_name, db_name, table_name ):
    con = sqlite3.connect(db_name)
    df_name[:0].to_sql(table_name, con,  if_exists='append', index=False)
    con.close() 


def db_last_row_to_df(db_name, table_name):
    con = sqlite3.connect(db_name)
    cur = con.cursor()
    query = cur.execute( "SELECT * FROM " + table_name + " ORDER BY rowid DESC LIMIT 1")
    cols = [column[0] for column in query.description]
    result = pd.DataFrame.from_records(data=query.fetchall(), columns=cols)
    con.close()
    return result    


def create_pickle(obj, filename):
    with open(filename, 'wb') as f:
        pk.dump(obj, f)


def read_pickle(filename):
    with open(filename, 'rb') as f:
        result = pk.load(f)
    return result


def api_infer(ip, df):
#     ip = "http://192.168.20.104:30266/"
    result = requests.post(ip+'api/info')
    result = eval(result.content.decode('utf-8'))
    model_id = list(result['models'].keys())[0]
    url = f"{ip}api/infer/{model_id}"
    json_data = {'data':df.to_dict(orient='records')}
    return eval(requests.post(url, json=json_data).content.decode('utf-8'))['result']


def create_stats_features(data, timewindow):
    mn = data.rolling(timewindow).min()
    mn.columns = [col + "_min" for col in mn.columns]

    mx = data.rolling(timewindow).max()
    mx.columns = [col + "_max" for col in mx.columns]

    means = data.rolling(timewindow).mean()
    means.columns = [col + "_mean" for col in means.columns]

    stds = data.rolling(timewindow).std()
    stds.columns = [col + "_std" for col in stds.columns]

    rnge = data.rolling(timewindow).apply(lambda x: max(x) - min(x))
    rnge.columns = [col + "_range" for col in rnge.columns]
    
    changes = data.rolling(timewindow).apply(lambda x: x[-1]-x[0])
    changes.columns = [col + "_change" for col in changes.columns]

    chg_rate = data.rolling(timewindow).apply(lambda x: abs(x[-1]-x[0])/x[0]  )
    chg_rate.columns = [col + "_chr" for col in chg_rate.columns]    
    
    result = pd.concat([mn, mx, means, stds, rnge, changes, chg_rate ], axis=1)
    return result


def create_corr_features(data, timewindow):
    comb_list = [list(i) for i in combinations(data.columns.tolist(),2)]
    result = pd.DataFrame(index=train.index)
    col_name = []
    for comb in comb_list:
        tmp = data[comb[0]].rolling(timewindow).corr(data[comb[1]])
        result = pd.concat([result, tmp], axis=1)
        col_name.append("_".join(comb)+"_corr")
    result.columns = col_name
    return result
