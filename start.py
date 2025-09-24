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
if 'Mid_vs_Entry' in entry_diff.columns:
    entry_diff['Mid_vs_Entry'] = entry_diff['Mid_vs_Entry'].map(lambda x: f"{x:.2f}")
#print(entry_diff[['Mid_vs_Entry']])
mid_diff = average_pay_df.pivot(index='job_title', columns='experience_level', values='average_salary')
mid_diff['Senior_vs_Mid'] = mid_diff['Senior'] - mid_diff['Mid']
if 'Senior_vs_Mid' in mid_diff.columns:
    mid_diff['Senior_vs_Mid'] = mid_diff['Senior_vs_Mid'].map(lambda x: f"{x:.2f}")
#print(mid_diff[['Senior_vs_Mid']])


query = get_query_by_label('queries.sql', 'count of job salary based on experience level and job title')
job_salary_count_df = pd.read_sql_query(query, conn)
#print(job_salary_count_df)#counts the number of jobs based on experience level
#safe for pdf report


# Print max salary by job title and experience level
query = get_query_by_label('queries.sql', 'max salary by job title and experience level')
max_salary_exp_df = pd.read_sql_query(query, conn)
if 'maximum_salary' in max_salary_exp_df.columns:
    max_salary_exp_df['maximum_salary'] = max_salary_exp_df['maximum_salary'].map(lambda x: f"{x:.2f}")
#print(max_salary_exp_df) #safe for pdf report

query = get_query_by_label('queries.sql', 'min salary by job title')
min_salary_df = pd.read_sql_query(query, conn)
if 'minimum_salary' in min_salary_df.columns:
    min_salary_df['minimum_salary'] = min_salary_df['minimum_salary'].map(lambda x: f"{x:.2f}")
#print(min_salary_df) #safe for pdf report

avg_salary_exp_df = pd.read_sql_query(query, conn)

query = get_query_by_label('queries.sql', 'average salary by job title and experience level')
avg_salary_exp_df = pd.read_sql_query(query, conn)
# Format average_salary column to two decimal places if it exists
if 'average_salary' in avg_salary_exp_df.columns:
	avg_salary_exp_df['average_salary'] = avg_salary_exp_df['average_salary'].map(lambda x: f"{x:.2f}")


with PdfPages('salary_report.pdf') as pdf:
	# Add a page with custom text
	plt.figure(figsize=(8.5, 11)) #page size
	plt.axis('off') #hide axes
	plt.text(0.5, 0.5, 'Salary Report\nGenerated using Data Science Salaries Dataset', horizontalalignment='center', verticalalignment='center', fontsize=24, color='black', wrap=True)
	pdf.savefig()
	plt.close()

	#display max and min salary by job title
	plt.figure(figsize=(8.5, 11)) #page size
	plt.axis('off') #hide axes
	plt.text(0.5, 1.03, 'Max Salary by Job Title', horizontalalignment='center', verticalalignment='top', fontsize=16, color='black', wrap=True)
	plt.table(cellText=max_salary_exp_df.values, colLabels=max_salary_exp_df.columns, cellLoc='center', loc='upper center')
	plt.text(0.5, 0.45, 'Min Salary by Job Title', horizontalalignment='center', verticalalignment='top', fontsize=16, color='black', wrap=True)
	plt.table(cellText=min_salary_df.values, colLabels=min_salary_df.columns, cellLoc='center', loc='lower center')
	pdf.savefig()
	plt.close()
	
	#display average salary by job title and experience level
	plt.figure(figsize=(8.5, 11)) #page size
	plt.axis('off') #hide axes
	plt.text(0.5, 1.03, 'Average Salary by Job Title and Experience Level', horizontalalignment='center', verticalalignment='top', fontsize=16, color='black', wrap=True)
	plt.table(cellText=avg_salary_exp_df.values, colLabels=avg_salary_exp_df.columns, cellLoc='center', loc='upper center')
	plt.text(0.5, 0.57, '*The average salary for entry and executive level Big Data, executive level for data scientist are not as accurate as other salaries given that the number of entries for these entries is lower.', horizontalalignment='center', verticalalignment='top', fontsize=8, color='black', wrap=True)
	pdf.savefig()
	plt.close()
	
	#display difference in pay between experience levels for each job title
	plt.figure(figsize=(8.5, 11)) #page size
	plt.axis('off') #hide axes
	plt.text(0.5, 1.03, 'Difference in Pay Between Experience Levels for Each Job Title', horizontalalignment='center', verticalalignment='top', fontsize=16, color='black', wrap=True)
	plt.table(cellText=entry_diff[['Mid_vs_Entry']].reset_index().values, colLabels=['Job Title', 'Mid vs Entry ($)'], cellLoc='center', loc='upper center')
	plt.table(cellText=mid_diff[['Senior_vs_Mid']].reset_index().values, colLabels=['Job Title', 'Senior vs Mid ($)'], cellLoc='center', loc='lower center')
	pdf.savefig()
	plt.close()