import pandas as pd
import sqlite3
import matplotlib.pyplot as plt
from utils import *
from matplotlib.backends.backend_pdf import PdfPages

#load csv data 
df = pd.read_csv('datascience_salaries.csv')

#create a new sqlite database (or connect to existing one)
conn = sqlite3.connect('salaries.db')


#delete duplicate rows 
df = remove_duplicates(df)

#delete columns from csv files -- used to clean up reference dataframes--
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

#-----------------------query data-----------------------

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

# Calculate differences and growth BEFORE formatting as string
entry_diff = average_pay_df.pivot(index='job_title', columns='experience_level', values='average_salary')
entry_diff['Mid_vs_Entry'] = entry_diff['Mid'] - entry_diff['Entry']
entry_diff['Growth_%'] = (entry_diff['Mid_vs_Entry'] / entry_diff['Entry'] * 100)
# Format for display
if 'Mid_vs_Entry' in entry_diff.columns:
	entry_diff['Mid_vs_Entry'] = entry_diff['Mid_vs_Entry'].map(lambda x: f"{x:.2f}")
if 'Growth_%' in entry_diff.columns:
	entry_diff['Growth_%'] = entry_diff['Growth_%'].map(lambda x: f"{x:.2f}%")

mid_diff = average_pay_df.pivot(index='job_title', columns='experience_level', values='average_salary')
mid_diff['Senior_vs_Mid'] = mid_diff['Senior'] - mid_diff['Mid']
mid_diff['Growth_%'] = (mid_diff['Senior_vs_Mid'] / mid_diff['Mid'] * 100)
if 'Senior_vs_Mid' in mid_diff.columns:
	mid_diff['Senior_vs_Mid'] = mid_diff['Senior_vs_Mid'].map(lambda x: f"{x:.2f}")
if 'Growth_%' in mid_diff.columns:
	mid_diff['Growth_%'] = mid_diff['Growth_%'].map(lambda x: f"{x:.2f}%")
#print(mid_diff)




query = get_query_by_label('queries.sql', 'count of job salary based on experience level and job title')
job_salary_count_df = pd.read_sql_query(query, conn)
#print(job_salary_count_df)#counts the number of jobs based on experience level
#safe for pdf report

# max salary by job title and experience level
query = get_query_by_label('queries.sql', 'max salary by job title and experience level')
max_salary_exp_df = pd.read_sql_query(query, conn)
if 'maximum_salary' in max_salary_exp_df.columns:
    max_salary_exp_df['maximum_salary'] = max_salary_exp_df['maximum_salary'].map(lambda x: f"{x:.2f}")
#print(max_salary_exp_df) #safe for pdf report

#min salary by job title and experience level
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

#------------------------generate pdf report-----------------------

with PdfPages('salary_report.pdf') as pdf:
	# Add a page with custom text
	plt.figure(figsize=(8.5, 11)) #page size
	plt.axis('off') #hide axes
	plt.text(0.5, 0.5, 
		  'Salary Report\nGenerated using Data Science Salaries Dataset', 
		  horizontalalignment='center', 
		  verticalalignment='center', 
		  fontsize=24, 
		  color='black', 
		  wrap=True)
	pdf.savefig()
	plt.close()

	fig, ax = plt.subplots(figsize=(8.5, 11)) #page size
	ax.axis('off') #hide axes
	ax.text(
		0.03, 0.5,  # x and y position with padding from left and top
		'This report provides only graphs and charts to better visualize the data and does not'
		' include any raw data tables. The findings come from the Data Science Salaries dataset'
		' found on Kaggle. The dataset includes salaries for various data science roles across '
		'different countries and experience levels. The report highlights key insights such as'
		' salary distributions, average salaries by job title and experience level, and '
		'differences in pay between experience levels.',
		ha='left',
		va='top',
		fontsize=20,
		color='black',
		wrap=True
	)
	fig.tight_layout(pad=2.0)
	pdf.savefig(fig)
	plt.close(fig)

	fig, ax = plt.subplots(figsize=(8.5, 5))
	ax.axis('off')
	ax.text(
		0.03,0.5,
		'The following pages will contain various graphs and charts that will ' \
		'show various insights derived from the dataset overall, insights regarding'\
		'regions and locations will follow.',
		ha='left',
		va = 'top',
		fontsize=16,
		color='black',
		wrap=True
	)
	fig.tight_layout(pad=2.0)
	pdf.savefig(fig)
	plt.close(fig)

	# Bar graph: job distribution by continent
	fig, ax = plt.subplots(figsize=(8.5, 5))
	continents = continent_df['continent']
	counts = continent_df['count']
	bars = ax.bar(continents, counts, color='skyblue')
	ax.set_title('Job Distribution by Continent', fontsize=18)
	ax.set_xlabel('Continent', fontsize=14)
	ax.set_ylabel('Number of Jobs', fontsize=14)
	ax.tick_params(axis='x', rotation=0)
	ax.set_position([0.1, 0.1, 0.8, 0.8])
	# Add value labels on top of each bar
	for bar in bars:
		height = bar.get_height()
		ax.annotate(f'{height}',
					xy=(bar.get_x() + bar.get_width() / 2, height),
					xytext=(0, 3),  # 3 points vertical offset
					textcoords="offset points",
					ha='center', va='bottom', fontsize=12, color='black')
	fig.tight_layout(pad=1.0)
	pdf.savefig(fig)
	plt.close(fig)

	plt.figure(figsize=(8.5, 11)) #page size
	plt.axis('off') #hide axes
	plt.text(0.5, 1.03, 
		  'Max Salary by Job Title', 
		  horizontalalignment='center', 
		  verticalalignment='top', 
		  fontsize=16, 
		  color='black', 
		  wrap=True)
	plt.table(cellText=max_salary_exp_df.values, 
		   colLabels=max_salary_exp_df.columns, 
		   cellLoc='center', 
		   loc='upper center')
	plt.text(0.5, 0.45, 
		  'Min Salary by Job Title', 
		  horizontalalignment='center', 
		  verticalalignment='top', 
		  fontsize=16, 
		  color='black', 
		  wrap=True)
	plt.table(cellText=min_salary_df.values, 
		   colLabels=min_salary_df.columns, 
		   cellLoc='center', 
		   loc='lower center')
	pdf.savefig()
	plt.close()
	
	#display average salary by job title and experience level
	plt.figure(figsize=(8.5, 11)) #page size
	plt.axis('off') #hide axes
	plt.text(0.5, 1.03, 
		  'Average Salary by Job Title and Experience Level', 
		  horizontalalignment='center', 
		  verticalalignment='top', 
		  fontsize=16, 
		  color='black', 
		  wrap=True)
	plt.table(
		cellText=avg_salary_exp_df.values, 
		colLabels=avg_salary_exp_df.columns, 
		cellLoc='center', loc='upper center')
	plt.text(0.5, 0.57, 
		  '*The average salary for entry and executive level Big Data, executive level for data scientist are not as accurate as other salaries given that the number of entries for these entries is lower.', 
		  horizontalalignment='center', 
		  verticalalignment='top', 
		  fontsize=8, 
		  color='black', 
		  wrap=True)
	pdf.savefig()
	plt.close()
	
	#display difference in pay between experience levels for each job title
	plt.figure(figsize=(8.5, 11)) #page size
	plt.axis('off') #hide axes
	plt.text(0.5, 1.03,
		   'Difference in Pay Between Experience Levels for Each Job Title', 
		   horizontalalignment='center', 
		   verticalalignment='top', 
		   fontsize=16, 
		   color='black', 
		   wrap=True)
	
	#table with entry level vs mid level salary differences
	table = plt.table(
		cellText=entry_diff[['Mid_vs_Entry', 'Growth_%']].reset_index().values, 
		colLabels=['Job Title', 'Mid vs Entry ($)', 'Growth (%)'], 
		cellLoc='center', 
		loc='upper center'
	)
	for row in range(1, len(mid_diff)+1):
		table[(row, 2)].set_facecolor("#1bd76c")  # light yellow

	plt.text(0.5, 0.8, 
		  'The job with the biggest jump between entry and mid level is:' \
		  '\n Data analyst with a 88.37% increase followed by Big Data with a 43.817% increase in average salary', 
		  horizontalalignment='center', 
		  verticalalignment='center', 
		  fontsize=16, 
		  color='black', 
		  wrap=True)
	#table with mid level vs senior level salary differences
	table = plt.table(
		cellText=mid_diff[['Senior_vs_Mid', 'Growth_%']].reset_index().values,
		colLabels=['Job Title', 'Senior vs Mid ($)', 'Growth (%)'],
		cellLoc='center',
		loc='center'
	)

	for row in range(1, len(mid_diff)+1):
		table[(row, 2)].set_facecolor("#1bd76c")  # light yellow

	plt.text(0.5, 0.4, 
		  'The job with the biggest jump between mid and senior level is:\n Data Scientist followed with a 72.45% increase in average salary followed by ML Ops with a 66.53% increase', 
		  horizontalalignment='center', 
		  verticalalignment='center', 
		  fontsize=16, 
		  color='black', 
		  wrap=True)
	pdf.savefig()
	plt.close()

##############	Australia  ############

	query = get_query_by_label('queries.sql', 'jobs based on a specific location')
	job_in_australia = pd.read_sql_query(query, conn, params=('Australia', None, None))
	
	query = get_query_by_label('queries.sql', 'job information based on specific location')
	info_australia = pd.read_sql_query(query, conn, params=('Australia',))


	fig,ax = plt.subplots(figsize=(8, 11))
	ax.axis('off')
	ax.text(0.5, 0.95,
		 'The following charts and graphs show the distribution of jobs'\
		 'in Australia and other insights.',
		 horizontalalignment='center',
		 verticalalignment='top',
		 fontsize=10,
		 color='black',
		 wrap=True)
	pdf.savefig(fig)
	plt.close(fig)

	#job distribution in Australia
	fig,ax = plt.subplots(figsize=(10,5))
	fig.text(0.5, 0.95,
		 'Job Distribution in Australia',
		 horizontalalignment='center',
		 verticalalignment='top',
		 fontsize=14,
		 color='black',
		 wrap=False)
	locations = job_in_australia['location']
	counts = job_in_australia['job_count']
	ax.pie(counts, labels=locations, autopct='%1.1f%%', startangle=140)
	pdf.savefig(fig)
	plt.close(fig)
	#info about australia jobs
	fig,ax = plt.subplots(figsize=(8.5, 11))
	ax.axis('off')
	ax.text(0.5, 0.95,
		 'Information about Jobs in Australia',
		 horizontalalignment='center',
		 verticalalignment='top',
		 fontsize=14,
		 color='black',
		 wrap=True)
	table = plt.table(
		cellText=info_australia.values,
		colLabels=info_australia.columns,
		cellLoc='center',
		loc='center'
	)
	pdf.savefig(fig)
	plt.close(fig)