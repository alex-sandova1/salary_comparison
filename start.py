import pandas as pd
import sqlite3

from utils import *

#load csv data 
df = pd.read_csv('datascience_salaries.csv')

#create a new sqlite database (or connect to existing one)
conn = sqlite3.connect('salaries.db')

#write the dataframe to a sql table named 'salaries'
df.to_sql('salaries', conn, if_exists='replace', index=False)

#deleete duplicate rows 
df = remove_duplicates(df)

#get the query for average salary for all scientists
query = get_query_by_label('queries.sql', 'average salary')
if query:
    result = pd.read_sql_query(query, conn)
    # Round the result to two decimal places and print just the value
    avg_salary = round(result.iloc[0, 0], 2)
    print(f"Average salary: {avg_salary}")
else:
    print("Query not found.")

print("\n")

#get the query for highest salary
query_highest = get_query_by_label('queries.sql', 'highest salary')
if query_highest:
    result_highest = pd.read_sql_query(query_highest, conn)
    print(result_highest.iloc[0])
else:
    print("Query not found.")

print("\n")

#get the query for lowest salary
query_lowest = get_query_by_label('queries.sql', 'lowest salary')
if query_lowest:
    result_lowest = pd.read_sql_query(query_lowest, conn)
    print(result_lowest.iloc[0])
else:
    print("Query not found.")

print("\n")

# Find average salary by job title
query_by_title = get_query_by_label('queries.sql', 'average salary by job title')
if query_by_title:
    df_by_title = pd.read_sql_query(query_by_title, conn)
    df_by_title['average_salary'] = df_by_title['average_salary'].round(2)    
    print("Average salary by job title:")
    print(df_by_title)
else:
    print("Query not found.")

#find how many employees per job title
employee_count = get_query_by_label('queries.sql', 'number of employees per job title')
if employee_count:
    result_employee_count = pd.read_sql_query(employee_count, conn)
    print("\nNumber of employees per job title:")
    print(result_employee_count)
else:
    print("Query not found.")

median = get_query_by_label('queries.sql', 'median salary')
if median:
    result_median = pd.read_sql_query(median, conn)
    print(result_median.iloc[0])
else:
    print("Query not found.")

#graph salary distribution
#plot_salary_distribution(df)



#plot_salary_distribution_by_title(df, 'Data scientist')

conn.close()