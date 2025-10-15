from utils import *
import pandas as pd
import sqlite3
import matplotlib.pyplot as plt

df = pd.read_csv('datascience_salaries.csv')

#create a new sqlite database (or connect to existing one)
conn = sqlite3.connect('salaries.db')

################# functions to test #################

query = get_query_by_label('queries.sql','jobs based on country on a specific continent')
test1 = pd.read_sql_query(query, conn)

################# graph functions #################


################## print results #################

print(test1)