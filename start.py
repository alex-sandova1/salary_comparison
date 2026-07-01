"""Salary Data Initialization and Report Generation

Initializes the salary database from CSV data and generates a comprehensive
PDF report with visualizations and summaries of job data by continent and country.

When run as the main script, this module:
1. Loads salary data from a CSV file
2. Removes duplicate records
3. Stores cleaned data in SQLite database
4. Generates a multi-page PDF report with charts and tables
"""
import pandas as pd
import sqlite3
import os
import matplotlib.pyplot as plt
from utils import *
from query import *
from matplotlib.backends.backend_pdf import PdfPages


# Configuration paths
DF_PATH = "datascience_salaries.csv"  # Source data file
DB_PATH = "salaries.db"              # SQLite database file
REPORT_PATH = "salary_report.pdf"    # Output PDF report file

# === DATA INITIALIZATION ===
# Load CSV data into memory
df = pd.read_csv(DF_PATH)
conn = sqlite3.connect(DB_PATH)

# Clean duplicates and persist to SQLite database
clean_df = remove_duplicates(df)
update_database(clean_df, conn, "salaries")

def main():
    """Generate the salary analysis PDF report. """
    # Generate report to a temp file, then atomically replace destination.
    temp_report_path = f"{REPORT_PATH}.tmp"
    try:
        pages_written = 0
        with PdfPages(temp_report_path) as pdf:
            # === PAGE 1: Continental Overview ===
            # Create chart showing job distribution across all continents
            location_df = group_location(conn, "continent")
            fig = plot_by_location(location_df, "continent")
            pdf.savefig(fig)
            pages_written += 1
            plt.close(fig)

            # === PAGES 2+: Country Details and Location Summaries ===
            # For each continent, create:
            # 1. Job count by country table
            # 2. Detailed summary by location/role/experience for each country
            continents = get_continents(conn)
            for continent in continents["continent"]:
                # Get all countries in this continent
                continent_df = count_jobs_by_country_in_continent(conn, continent)
            
                # Table: Job count by country for this continent
                figs = table_pages_by_location(
                    continent_df,
                    "country",
                    title=f"Job Count by Country - {continent}",
                    rows_per_page=28,
                )
                for fig in figs:
                    pdf.savefig(fig)
                    pages_written += 1
                    plt.close(fig)
            
                # Detailed summary tables: For each country in this continent
                country_names = continent_df["location"].dropna().unique()
                for country in country_names:
                    summary_df = job_summary_by_location_in_country(conn, country)
                    summary_figs = table_by_country_location_summary(
                        summary_df,
                        title=f"Job Summary by Location in {country}",
                        rows_per_page=28,
                    )
                    for fig in summary_figs:
                        pdf.savefig(fig)
                        pages_written += 1
                        plt.close(fig)
        
        # Verify that at least some pages were generated
        if pages_written == 0:
            raise RuntimeError("No report pages were generated.")

        # Atomically replace the destination file with the completed temp file
        os.replace(temp_report_path, REPORT_PATH)
    except Exception:
        # Clean up temp file if generation failed
        if os.path.exists(temp_report_path):
            os.remove(temp_report_path)
        raise
        
    

if __name__ == "__main__":
    main()
    