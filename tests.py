import sqlite3
import pandas as pd
from unittest.mock import patch
from utils import *

# Test remove_duplicates
df = pd.DataFrame({'a': [1, 1, 2], 'b': [3, 3, 4]})
result = remove_duplicates(df)
assert len(result) == 2, "Should have 2 rows after removing duplicate"
print("remove_duplicates: PASSED")

# Test get_query_by_label
sql = get_query_by_label("queries.sql", "average salary")
assert sql is not None, "Should find the query"
print("get_query_by_label: PASSED")

# Test update_database
conn = sqlite3.connect(":memory:")  # in-memory, nothing saved to disk
update_database(df, conn, "test_table")
result = pd.read_sql_query("SELECT * FROM test_table", conn)
assert len(result) == 3
print("update_database: PASSED")
conn.close()

# Fake data
salary_df = pd.DataFrame({
    'salary': [50000, 60000, 70000, 80000],
    'job_title': ['Data Analyst', 'Data Analyst', 'Data Scientist', 'Data Scientist']
})

continent_df = pd.DataFrame({
    'continent': ['Asia', 'Asia', 'Europe'],
    'salary': [50000, 60000, 70000],
    'count': [10, 20, 15]
})

with patch('matplotlib.pyplot.show'):
    plot_salary_distribution(salary_df)
    print("plot_salary_distribution: PASSED")

    plot_salary_distribution_by_title(salary_df, 'Data Analyst')
    print("plot_salary_distribution_by_title: PASSED")

    bar_distribution_by_location(continent_df, 'Asia')
    print("bar_distribution_by_location: PASSED")