import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

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

def plot_by_continent(df):
    return plot_by_location(df, "continent")