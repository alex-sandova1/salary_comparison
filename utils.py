import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
from matplotlib.figure import Figure
import pandas as pd

def plot_by_location(df, location):
    """Create a bar chart of job counts grouped by a location level."""
    location_label = location.strip().capitalize()
    fig, ax = plt.subplots(figsize=(10, 6))
    df.plot(kind='bar', x='location', y='job_count', legend=False, ax=ax)
    ax.set_title(f'Job Count by {location_label}')
    ax.set_xlabel(location_label)
    ax.set_ylabel('Count')
    ax.tick_params(axis='x', rotation=45)
    
    # Add value labels on top of bars
    for container in ax.containers:
        ax.bar_label(container, fmt='%.0f', padding=3)
        
    # Set y-axis limit with 20% padding at top
    max_count = df["job_count"].max()
    ax.set_ylim(0, max_count * 1.2)
    fig.tight_layout()
    return fig

def table_pages_by_location(df, location, title=None, rows_per_page=28):
    """Create multi-page PDF table figures showing job counts by location."""
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

def plot_by_continent(df):
    """Create a bar chart of job counts grouped by continent."""
    return plot_by_location(df, "continent")

def table_by_country(df, title=None, rows_per_page=28):
    """Create multi-page PDF table figures showing job counts by country."""
    return table_pages_by_location(df, "country", title=title, rows_per_page=rows_per_page)

def table_by_country_location_summary(df, title=None, rows_per_page=28):
    """Create multi-page PDF table figures showing detailed job summary by location within a country. """
    # Select and rename columns for display
    table_df = df[["location", "job_title", "experience_level", "job_count", "avg_salary"]].copy()
    table_df.columns = ["Location", "Job Title", "Experience", "Job Count", "Avg Salary"]
    table_df["Avg Salary"] = table_df["Avg Salary"].round(2)

    figures = []
    total_pages = (len(table_df) + rows_per_page - 1) // rows_per_page

    for page_idx in range(total_pages):
        start = page_idx * rows_per_page
        end = start + rows_per_page
        page_df = table_df.iloc[start:end]

        # Landscape A3 format for detailed summary with many columns
        fig, ax = plt.subplots(figsize=(11.69, 8.27))
        ax.axis("off")

        page_title = title or "Job Summary by Location"
        if total_pages > 1:
            page_title = f"{page_title} (Page {page_idx + 1}/{total_pages})"

        ax.set_title(page_title, fontsize=13, y=0.98)

        # Adjust table height based on number of rows
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


def pie_graph(df, figsize=(5.4, 4.5), dpi=100):
    """Create a pie chart showing job distribution by location."""
    fig = Figure(figsize=figsize, dpi=dpi, facecolor="#FFFFFF")
    ax = fig.add_subplot(111)
    ax.set_facecolor("#FFFFFF")

    # Handle empty dataframe
    if df.empty:
        ax.text(0.5, 0.5, "No data available", ha="center", va="center", fontsize=12)
        ax.axis("off")
        return fig
    
    # Extract data and create pie chart
    values = df["job_count"].tolist()
    labels = df["location"].tolist()

    total = sum(values)

    def percentage_label(pct):
        """Avoid unreadable labels on the smallest pie slices."""
        return f"{pct:.1f}%" if pct >= 4 else ""

    wedges, _, _ = ax.pie(
        values,
        autopct=percentage_label,
        startangle=140,
        colors=["#173F5F", "#E76F51", "#2A9D8F", "#E9C46A", "#6C8EAD", "#B56576", "#8AB17D"],
        textprops={"color": "#243B53", "fontsize": 9, "weight": "bold"},
        wedgeprops={"linewidth": 1, "edgecolor": "white"},
        pctdistance=0.70,
    )
    legend_labels = [f"{label}  ({value / total:.1%})" for label, value in zip(labels, values)]
    ax.legend(
        wedges,
        legend_labels,
        title="Country",
        loc="center left",
        bbox_to_anchor=(1.02, 0.5),
        frameon=False,
        labelspacing=0.8,
        fontsize=8,
        title_fontsize=9,
    )
    ax.set_title("Job count distribution", fontsize=12, fontweight="bold", color="#243B53", pad=12)
    fig.tight_layout()
    return fig


def get_salary_stats(df, conn=None):
    """Extract salary statistics from a dataframe."""
    # Handle empty or missing salary data
    if df.empty or "salary" not in df.columns:
        return {"avg_salary": 0, "highest_pay": None, "lowest_pay": None}

    # Convert salary to numeric and remove missing values
    df_copy = df.copy()
    df_copy["salary"] = pd.to_numeric(df_copy["salary"], errors="coerce")
    df_copy = df_copy.dropna(subset=["salary"])

    # Handle case where all salaries were invalid
    if df_copy.empty:
        return {"avg_salary": 0, "highest_pay": None, "lowest_pay": None}

    # Calculate statistics
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
