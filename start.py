import pandas as pd
import sqlite3
import os
import matplotlib.pyplot as plt
from utils import *
from query import *
from matplotlib.backends.backend_pdf import PdfPages


# Load CSV data
DF_PATH = "datascience_salaries.csv"
DB_PATH = "salaries.db"
REPORT_PATH = "salary_report.pdf"


df = pd.read_csv(DF_PATH)
conn = sqlite3.connect(DB_PATH)

# Clean duplicates and persist to SQLite
clean_df = remove_duplicates(df)
update_database(clean_df, conn, "salaries")

def main():
    # Generate report to a temp file, then atomically replace destination.
    temp_report_path = f"{REPORT_PATH}.tmp"
    try:
        pages_written = 0
        with PdfPages(temp_report_path) as pdf:
            location_df = group_location(conn, "continent")
            fig = plot_by_location(location_df, "continent")
            pdf.savefig(fig)
            pages_written += 1
            plt.close(fig)

            # Generate tables for each continent
            continents = get_continents(conn)
            for continent in continents["continent"]:
                continent_df = count_jobs_by_country_in_continent(conn, continent)
            
                # existing country-count table for this continent
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
            
                # new: cycle each country in this continent
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
        

        if pages_written == 0:
            raise RuntimeError("No report pages were generated.")

        os.replace(temp_report_path, REPORT_PATH)
    except Exception:
        if os.path.exists(temp_report_path):
            os.remove(temp_report_path)
        raise
        
    

if __name__ == "__main__":
    main()
    