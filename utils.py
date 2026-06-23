import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.figure import Figure
import pandas as pd

#plots data based on location
def plot_by_location(df, location):
    location_label = location.strip().capitalize()
    fig, ax = plt.subplots(figsize=(10, 6))
    df.plot(kind='bar', x='location', y='job_count', legend=False, ax=ax)
    ax.set_title(f'Job Count by {location_label}')
    ax.set_xlabel(location_label)
    ax.set_ylabel('Count')
    ax.tick_params(axis='x', rotation=45)
    
    for container in ax.containers:
        ax.bar_label(container, fmt='%.0f', padding=3)
        
    max_count = df["job_count"].max()
    ax.set_ylim(0, max_count * 1.2)
    fig.tight_layout()
    return fig

#plots tables based on location
def table_pages_by_location(df, location, title=None, rows_per_page=28):
    location_label = location.strip().capitalize()
    table_df = df[["location", "job_count"]].copy()
    table_df.columns = [location_label, "Job Count"]

    figures = []
    total_pages = (len(table_df) + rows_per_page - 1) // rows_per_page

    for page_idx in range(total_pages):
        start = page_idx * rows_per_page
        end = start + rows_per_page
        page_df = table_df.iloc[start:end]

        # A4 portrait size; gives more vertical space for long tables
        fig, ax = plt.subplots(figsize=(8.27, 11.69))
        ax.axis("off")

        page_title = title or f"Job Count by {location_label}"
        if total_pages > 1:
            page_title = f"{page_title} (Page {page_idx + 1}/{total_pages})"

        ax.set_title(page_title, fontsize=13, y=0.98)

        # Keep short tables compact instead of stretching them to fill the page.
        n_rows = len(page_df)
        table_height = min(0.82, max(0.18, 0.06 + n_rows * 0.03))
        top_margin = 0.12
        bottom_margin = 0.06
        y0 = bottom_margin + ((1 - top_margin - bottom_margin) - table_height) / 2

        table = ax.table(
            cellText=page_df.values,
            colLabels=page_df.columns,
            cellLoc="center",
            colLoc="center",
            # Leaves top margin so title does not overlap table
            bbox=[0.05, y0, 0.90, table_height],
        )

        table.auto_set_font_size(False)
        table.set_fontsize(9)
        table.scale(1, 1.0)

        figures.append(fig)

    return figures

#plots data based on continent
def plot_by_continent(df):
    return plot_by_location(df, "continent")

#creates table to display data based on country
def table_by_country(df, title=None, rows_per_page=28):
    return table_pages_by_location(df, "country", title=title, rows_per_page=rows_per_page)

def table_by_country_location_summary(df, title=None, rows_per_page=28):
    table_df = df[["location", "job_title", "experience_level", "job_count", "avg_salary"]].copy()
    table_df.columns = ["Location", "Job Title", "Experience", "Job Count", "Avg Salary"]
    table_df["Avg Salary"] = table_df["Avg Salary"].round(2)

    figures = []
    total_pages = (len(table_df) + rows_per_page - 1) // rows_per_page

    for page_idx in range(total_pages):
        start = page_idx * rows_per_page
        end = start + rows_per_page
        page_df = table_df.iloc[start:end]

        fig, ax = plt.subplots(figsize=(11.69, 8.27))
        ax.axis("off")

        page_title = title or "Job Summary by Location"
        if total_pages > 1:
            page_title = f"{page_title} (Page {page_idx + 1}/{total_pages})"

        ax.set_title(page_title, fontsize=13, y=0.98)

        n_rows = len(page_df)
        table_height = min(0.82, max(0.18, 0.06 + n_rows * 0.03))
        top_margin = 0.12
        bottom_margin = 0.06
        y0 = bottom_margin + ((1 - top_margin - bottom_margin) - table_height) / 2

        table = ax.table(
            cellText=page_df.values,
            colLabels=page_df.columns,
            cellLoc="center",
            colLoc="center",
            bbox=[0.03, y0, 0.94, table_height],
        )

        table.auto_set_font_size(False)
        table.set_fontsize(8)
        table.scale(1, 1.0)

        figures.append(fig)

    return figures


def pie_graph(df, figsize=(4.2, 4.5), dpi=100):
    fig = Figure(figsize=figsize, dpi=dpi)
    ax = fig.add_subplot(111)

    if df.empty:
        ax.text(0.5, 0.5, "No data available", ha="center", va="center", fontsize=12)
        ax.axis("off")
        return fig
    
    values = df["job_count"].tolist()
    labels = df["location"].tolist()

    ax.pie(
        values,
        labels=labels,
        autopct="%1.1f%%",
        startangle=140,
        wedgeprops={"linewidth": 1, "edgecolor": "white"},
    )
    ax.set_title("Job Count Distribution", fontsize=12)
    fig.tight_layout()
    return fig


def get_salary_stats(df, conn=None):
    """
    Extract salary statistics from a dataframe.
    Returns dict with: avg_salary, highest_pay (row), lowest_pay (row)
    """
    if df.empty or "salary" not in df.columns:
        return {"avg_salary": 0, "highest_pay": None, "lowest_pay": None}

    # Convert salary to numeric
    df_copy = df.copy()
    df_copy["salary"] = pd.to_numeric(df_copy["salary"], errors="coerce")
    df_copy = df_copy.dropna(subset=["salary"])

    if df_copy.empty:
        return {"avg_salary": 0, "highest_pay": None, "lowest_pay": None}

    avg_salary = df_copy["salary"].mean()
    highest_idx = df_copy["salary"].idxmax()
    lowest_idx = df_copy["salary"].idxmin()

    highest_pay = df_copy.loc[highest_idx].to_dict()
    lowest_pay = df_copy.loc[lowest_idx].to_dict()

    return {
        "avg_salary": avg_salary,
        "highest_pay": highest_pay,
        "lowest_pay": lowest_pay,
    }