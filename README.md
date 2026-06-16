# Salary Comparison Portfolio Project

An end-to-end data storytelling project that transforms raw salary records into a clean, stakeholder-friendly PDF report.

This project demonstrates a practical analytics workflow: data cleaning, SQL modeling, query-driven analysis, and visual report generation using Python.

## Project Snapshot

- Goal: surface global hiring and compensation patterns in data science roles.
- Input: `datascience_salaries.csv`.
- Processing stack: pandas + SQLite.
- Output: `salary_report.pdf` with chart and paginated insight tables.

## Why This Project Matters

Instead of stopping at notebook exploration, this project packages analysis into a repeatable reporting pipeline. It is built to answer real-world questions like:

- Which continents have the highest concentration of data roles?
- How do job counts vary by country within each continent?
- Within each country, how do location, role title, and experience level relate to average salary?

## What The Pipeline Produces

Running the project generates a report with:

- A bar chart of job count by continent.
- Paginated country tables for each continent (job count by country).
- Paginated location summaries for each country, including:
  - location
  - job title
  - experience level
  - job count
  - average salary

To prevent partial outputs, report pages are written to a temporary file and moved into place only after successful completion.

## Technical Highlights

- Data quality step: duplicate record removal before persistence.
- SQL abstraction: labeled query blocks loaded dynamically from `queries.sql`.
- Reproducible storage: SQLite table refresh on each run.
- Automated document generation: matplotlib figures exported to a multi-page PDF.
- Scalable presentation: long tables are paginated for readability.

## Architecture

- `start.py` orchestrates the full workflow (CSV -> SQLite -> PDF).
- `query.py` handles SQL loading plus data retrieval/transformation helpers.
- `utils.py` builds chart and table figures for the report.
- `queries.sql` stores reusable labeled SQL statements.
- `tests.py` provides manual exploratory checks for selected functions.

## Skills Demonstrated

- Data cleaning and preparation with pandas
- Relational querying with SQLite
- Analytical aggregation by geography and role metadata
- Programmatic report generation with matplotlib
- Scripted, repeatable analytics delivery

## Run Locally

Requirements:

- Python 3.10+
- pandas
- matplotlib

Install dependencies:

```bash
pip install -r requirements.txt
```

Run from the project root:

```bash
python start.py
```

Generated artifacts:

- `salaries.db`
- `salary_report.pdf`

## Current Testing State

`tests.py` is currently a manual script for spot-checking query outputs and table rendering. Converting this to an automated test suite is a planned improvement.
