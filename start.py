import pandas as pd
import sqlite3
import math

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

#work on pdf report
 
#add number of jobs per country and continent to pdf report
with PdfPages('salary_report.pdf') as pdf:
    mid = math.floor(len(country_df) / 2)
    first_half = country_df.iloc[:mid, :]
    second_half = country_df.iloc[mid:, :]

    # Create a figure for the first half
    plt.figure(figsize=(8, 6))
    plt.axis('off')
    plt.title('Job Count by Country (First Half)', fontsize=16)
    table = plt.table(cellText=first_half.values, colLabels=first_half.columns, cellLoc='left', loc='center left', colWidths=[0.3, 0.2])
    table.auto_set_font_size(True)
    table.set_fontsize(8)
    table.scale(0.8, 0.8)
    pdf.savefig()
    plt.close()

    # Create a figure for the second half
    plt.figure(figsize=(8, 6))
    plt.axis('off')
    plt.title('Job Count by Country (Second Half)', fontsize=16)
    table = plt.table(cellText=second_half.values, colLabels=second_half.columns, cellLoc='left', loc='center left', colWidths=[0.3, 0.2])
    table.auto_set_font_size(True)
    table.set_fontsize(8)
    table.scale(0.8, 0.8)
    pdf.savefig()
    plt.close()
