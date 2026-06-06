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
africa_grouped =jobs_by_continent(conn, "Africa")
print(africa_grouped, "\n")

#get job titles by country
africa_by_country = jobs_by_country(conn, "South Africa")
print(africa_by_country, "\n")

#get job titles by location
africa_by_location = jobs_by_location(conn, "Cape Town")
print(africa_by_location, "\n")

#get average salary by location
#africa_avg = avg_salary_by_location(africa_grouped, location_col="location", salary_col="salary")
#print(africa_avg, "\n")

#get job count by country in continent
#africa_job_count = count_jobs_by_country_in_continent(conn, "Africa")
#print(africa_job_count, "\n")

#africa_highest_paid = highest_paying_job_by_location(africa_grouped, location_col="location", job_col="job_title", salary_col="salary")
#print(africa_highest_paid, "\n")

