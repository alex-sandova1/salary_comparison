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

#test table by country location summary using job_summary_by_location_in_country query result as input
job_summary = job_summary_by_location_in_country(conn, "South Africa")
country_location_summary_figs = table_by_country_location_summary(job_summary, title="Job Summary by Location in South Africa", rows_per_page=28)
for fig in country_location_summary_figs:
    fig.show()