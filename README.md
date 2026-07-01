# Salary Comparison Portfolio Project

End-to-end salary analysis project built with pandas, SQLite, matplotlib, and Tkinter.

The project loads data science salary records, removes duplicates, writes cleaned data to SQLite, and provides two ways to explore insights:

- A generated multi-page PDF report
- A desktop GUI for interactive drill-down by continent and country

## Project Goals

This workflow is designed to answer practical questions such as:

- Which continents have the largest concentration of roles?
- How does job volume vary by country inside each continent?
- Inside a selected country, how do location, role, and experience level relate to average salary?

## Data Flow

1. Read raw CSV from `datascience_salaries.csv`
2. Remove duplicate rows
3. Replace the `salaries` table in `salaries.db`
4. Run labeled SQL queries from `queries.sql`
5. Render outputs as PDF pages and/or interactive GUI tables/charts

## Outputs

Running `start.py` generates:

- `salaries.db`
- `salary_report.pdf`

The report includes:

- Bar chart: job count by continent
- Country tables by continent (paginated)
- Country-level summary tables (paginated) with:
  - location
  - job title
  - experience level
  - job count
  - average salary

The PDF is written to a temporary file first and then atomically replaced, preventing partial/corrupted report files if generation fails.

## Interactive GUI

`gui.py` provides a Tkinter app that reads from `salaries.db` and supports:

- Home screen with continent buttons
- Continent view:
  - Overall job-count table by country
  - Country selector for detailed drill-down
- Data view:
  - Table results
  - Pie chart for overall country distribution
  - Salary summary cards (average, highest, lowest)

Important: run `start.py` at least once before starting the GUI so `salaries.db` and the `salaries` table exist.

## File Overview

- `start.py`: Pipeline entry point (CSV -> SQLite -> PDF)
- `gui.py`: Interactive Tkinter desktop interface
- `query.py`: SQL loader and query helper functions
- `queries.sql`: Labeled SQL statements used by query helpers
- `utils.py`: Plotting, paginated table rendering, pie chart, salary stats helpers
- `tests.py`: Manual script for exploratory spot checks
- `Reference/`: Extra location reference CSV files

## Setup

Requirements:

- Python 3.10+

Install dependencies:

```bash
pip install -r requirements.txt
```

## Usage

Generate database and PDF report:

```bash
python start.py
```

Run the GUI app:

```bash
python gui.py
```

Optional manual checks:

```bash
python tests.py
```

## Current Limitations

- `tests.py` is not an automated unit/integration test suite yet.
- SQL query lookup is based on label matching in comments, so label naming consistency in `queries.sql` is important.

## Tech Stack

- pandas
- sqlite3
- matplotlib
- tkinter
