import sqlite3
import pandas as pd
from utils import *
from query import *

# Load CSV data
DF_PATH = "datascience_salaries.csv"
DB_PATH = "salaries.db"
REPORT_PATH = "salary_report.pdf"


df = pd.read_csv(DF_PATH)
conn = sqlite3.connect(DB_PATH)

#test will be done using Africa as paramter for the location query

#get jobs titles
africa_grouped =jobs_by_location(conn, "Africa")
print(africa_grouped, "\n")

#get average salary by location
africa_avg = avg_salary_by_location(africa_grouped, location_col="location", salary_col="salary")
print(africa_avg, "\n")