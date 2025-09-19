import pandas as pd
import sqlite3

from utils import *
from matplotlib.backends.backend_pdf import PdfPages



#load csv data 
df = pd.read_csv('datascience_salaries.csv')

#create a new sqlite database (or connect to existing one)
conn = sqlite3.connect('salaries.db')

#write the dataframe to a sql table named 'salaries'
df.to_sql('salaries', conn, if_exists='replace', index=False)
 
#delete duplicate rows 
df = remove_duplicates(df)

#get jobs based on location
query = get_query_by_label('queries.sql', 'jobs based on location')
location_df = pd.read_sql_query(query, conn)
print(location_df)

#remote jobs
query = get_query_by_label('queries.sql', 'remote jobs')
remote_df = pd.read_sql_query(query, conn)
print(remote_df)

#create csv that will contain location and number of jobs
location = location_df['location'].value_counts().reset_index()
location.columns = ['location', 'job_count']
location.to_csv('location.csv', index=False)

#delete state_id column from cities.csv
cities = pd.read_csv('Location info/cities.csv')
cities = cities.drop(columns=['state_id'])
cities.to_csv('Location info/cities.csv', index=False)

conn.close()