import pandas as pd
import sqlite3

from utils import *
from matplotlib.backends.backend_pdf import PdfPages



#load csv data 
df = pd.read_csv('datascience_salaries.csv')

#create a new sqlite database (or connect to existing one)
conn = sqlite3.connect('salaries.db')


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
'''location = location_df['location'].value_counts().reset_index()
location.columns = ['location', 'job_count']
location.to_csv('location.csv', index=False)'''

#delete columns from csv files
'''cities = pd.read_csv('cities.csv')
cities = cities.drop(columns=['latitude', 'longitude'])
cities.to_csv('cities.csv', index=False)

states = pd.read_csv('states.csv')
states = states.drop(columns=['latitude', 'longitude'])
states.to_csv('states.csv', index=False)

countries = pd.read_csv('countries.csv')
countries = countries.drop(columns=['emoji', 'emojiU','longitude', 'latitude','timezones','native','tld','currency_symbol','currency','capital','phone_code'])
countries.to_csv('countries.csv', index=False)
conn.close()
'''
#print jobs based on country
query = get_query_by_label('queries.sql', 'jobs based on country')
country_df = pd.read_sql_query(query, conn)
print(country_df)