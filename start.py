import pandas as pd
import sqlite3
import math
import matplotlib.pyplot as plt

from utils import *
from matplotlib.backends.backend_pdf import PdfPages

#load csv data 
df = pd.read_csv('datascience_salaries.csv')

#create a new sqlite database (or connect to existing one)
conn = sqlite3.connect('salaries.db')


#delete duplicate rows 
df = remove_duplicates(df)

#delete columns from csv files -- used to clean up reference dataframes
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

#update db with new dataframe
update_database(df, conn, 'salaries') #call when needed

#print jobs based on country
query = get_query_by_label('queries.sql', 'jobs based on country')
country_df = pd.read_sql_query(query, conn)
#print(country_df)

#print jobs based by continent
query = get_query_by_label('queries.sql', 'jobs based on continent')
continent_df = pd.read_sql_query(query, conn)
#print(continent_df.head())

#print(continent_df.columns)

query = get_query_by_label('queries.sql', 'experience level distribution  grouped by country then experience level')
experience_df = pd.read_sql_query(query, conn)
#print(experience_df)

query = get_query_by_label('queries.sql', 'average pay by job based on experience level')
average_pay_df = pd.read_sql_query(query, conn)
#print(average_pay_df)#data is broken down by job title and experience level
#safe for pdf report

#calculate difference in pay between experience levels for each job title
entry_diff = average_pay_df.pivot(index='job_title', columns='experience_level', values='average_salary')
entry_diff['Mid_vs_Entry'] = entry_diff['Mid'] - entry_diff['Entry']
print(entry_diff[['Mid_vs_Entry']])
mid_diff = average_pay_df.pivot(index='job_title', columns='experience_level', values='average_salary')
mid_diff['Senior_vs_Mid'] = mid_diff['Senior'] - mid_diff['Mid']
print(mid_diff[['Senior_vs_Mid']])


query = get_query_by_label('queries.sql', 'count of job salary based on experience level and job title')
job_salary_count_df = pd.read_sql_query(query, conn)
#print(job_salary_count_df)#counts the number of jobs based on experience level
#safe for pdf report