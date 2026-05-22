import pandas as pd
import sqlite3
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
    # Generate report
    with PdfPages(REPORT_PATH) as pdf:
        location_df = group_location(conn, "continent")
        fig = plot_by_location(location_df, "continent")
        pdf.savefig(fig)  # Save the current figure into the PDF))
        # Generate tables for each continent
        continents = get_continents(conn)
        for continent in continents["continent"]:
            continent_df = count_jobs_by_country_in_continent(conn, continent)
            figs = table_pages_by_location(
                continent_df,
                "country",
                title=f"Job Count by Country - {continent}",
                rows_per_page=28,
            )
            for fig in figs:
                pdf.savefig(fig)
                plt.close(fig)
        
    

if __name__ == "__main__":
    main()
    