from utils import *
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt

df = pd.read_csv('datascience_salaries.csv')

#create a new sqlite database (or connect to existing one)
conn = sqlite3.connect('salaries.db')

################# functions to test #################

query = get_query_by_label('queries.sql', 'jobs based on country on a specific location')
params = ('North America', None, None)
test1 = pd.read_sql_query(query, conn, params=params)

query = get_query_by_label('queries.sql','jobs based on country on a specific location')
params = (None, 'United States', None)
test2 = pd.read_sql_query(query, conn, params=params)

query = get_query_by_label('queries.sql','jobs based on country on a specific location')
params = (None, None, 'San Francisco')
test3 = pd.read_sql_query(query, conn, params=params)

################# graph functions #################


################## print results #################

print(test1)
print("------------------\n")
print(test2)
print("------------------\n")
print(test3)
print("------------------\n")