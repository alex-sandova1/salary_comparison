import pandas as pd
import sqlite3

df = pd.read_csv('datascience_salaries.csv')

conn = sqlite3.connect('salaries.db')

df.to_sql('salaries', conn, if_exists='replace', index=False)

query = "SELECT AVG(salary) AS average_salary FROM salaries;"

result = pd.read_sql_query(query, conn)

print(result)

conn.close()