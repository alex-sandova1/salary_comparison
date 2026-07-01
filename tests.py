import sqlite3
import pandas as pd
from utils import *
from query import *

# === DATABASE SETUP ===
# Configuration paths
DF_PATH = "datascience_salaries.csv"
DB_PATH = "salaries.db"
REPORT_PATH = "salary_report.pdf"

# Load data and establish connection
df = pd.read_csv(DF_PATH)
conn = sqlite3.connect(DB_PATH)

# === TEST QUERIES ===
# Testing with Africa as the example continent and South Africa as the example country

# Test 1: Get all job records for a continent
print("TEST 1: Get job titles and salaries for Africa")
africa_grouped = jobs_by_continent(conn, "Africa")
print(africa_grouped, "\n")

# Test 2: Get job records for a specific country
print("TEST 2: Get job titles and salaries for South Africa")
africa_by_country = jobs_by_country(conn, "South Africa")
print(africa_by_country, "\n")

# Test 3: Get job records for a specific location
print("TEST 3: Get job titles and salaries for Cape Town")
africa_by_location = jobs_by_location(conn, "Cape Town")
print(africa_by_location, "\n")

# Test 4: Generate a detailed summary table and visualize it as multi-page PDF figures
print("TEST 4: Generate job summary by location in South Africa and display as table figures")
job_summary = job_summary_by_location_in_country(conn, "South Africa")
country_location_summary_figs = table_by_country_location_summary(
    job_summary, 
    title="Job Summary by Location in South Africa", 
    rows_per_page=28
)
for fig in country_location_summary_figs:
    fig.show()