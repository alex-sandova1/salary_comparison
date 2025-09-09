import pandas as pd
import sqlite3

df = pd.read_csv('datascience_salaries.csv')

conn = sqlite3.connect('salaries.db')

df.to_sql('salaries', conn, if_exists='replace', index=False)

#grab average salary for data scientist
query = "SELECT AVG(salary) AS average_salary FROM salaries WHERE job_title = 'Data scientist';"
result = pd.read_sql_query(query, conn)
Ds_avg = result['average_salary'][0]

#grab average salary for
print(f"Average salary for Data Scientist: {Ds_avg}")

#print(result)

conn.close()