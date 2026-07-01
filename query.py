import pandas as pd


def get_query_by_label(filename, label):
    """Extract a specific SQL query from a file using a label prefix."""
    with open(filename, "r") as f:
        content = f.read()

    queries = content.split("--")
    for q in queries:
        lines = q.strip().splitlines()
        if not lines:
            continue

        comment = lines[0].strip().lower()
        sql = "\n".join(lines[1:]).strip()

        if label.lower() in comment and sql:
            if sql.endswith(";"):
                sql = sql[:-1]
            return sql

    return None

def remove_duplicates(df):
    """Remove duplicate rows from a DataFrame based on all columns."""
    return df.drop_duplicates()

def update_database(df, conn, table_name):
    """Write a DataFrame to the database, replacing the entire table. """
    df.to_sql(table_name, conn, if_exists="replace", index=False)
    conn.commit()

def group_location(conn, location):
    """Query jobs grouped by a specific location hierarchy level."""
    location_key = location.strip().lower()
    if location_key not in {"continent", "country", "location"}:
        raise ValueError("location must be one of: continent, country, location")

    sql_template = get_query_by_label("queries.sql", "jobs by location")
    sql = sql_template.format(location=location_key)
    return pd.read_sql_query(sql, conn)

def group_country(conn, continent):
    """Query jobs grouped by country within a continent."""
    sql_template = get_query_by_label("queries.sql", "jobs by country in continent")
    return pd.read_sql_query(sql_template, conn, params=[continent])

def count_jobs_by_country_in_continent(conn, continent):
    """Query job counts grouped by country within a continent. """
    return group_country(conn, continent)

def get_continents(conn):
    """Retrieve list of all continents in the database. """
    sql_template = get_query_by_label("queries.sql", "continent list")
    return pd.read_sql_query(sql_template, conn)

def jobs_by_continent(conn, continent):
    """Query job records for a specific continent."""
    get_query_template = get_query_by_label("queries.sql", "jobs by continent")
    return pd.read_sql_query(get_query_template, conn, params=[continent])

def jobs_by_country(conn, country):
    """Query job records for a specific country."""
    get_query_template = get_query_by_label("queries.sql", "jobs by country")
    return pd.read_sql_query(get_query_template, conn, params=[country])

def jobs_by_country(conn, country):
    """Query job records for a specific country."""
    get_query_template = get_query_by_label("queries.sql", "job by country")
    return pd.read_sql_query(get_query_template, conn, params=[country])

def jobs_by_location(conn, location):
    """Query job records for a specific location (states, cities, etc.)."""
    get_query_template = get_query_by_label("queries.sql", "job by location")
    return pd.read_sql_query(get_query_template, conn, params=[location])

def avg_salary_by_location(df, location_col="location", salary_col="salary"):
    """Calculate average salary grouped by location from a job query result."""
    if location_col not in df.columns or salary_col not in df.columns:
        raise ValueError("DataFrame must include location and salary columns")

    work = df[[location_col, salary_col]].copy()
    work[salary_col] = pd.to_numeric(work[salary_col], errors="coerce")
    work = work.dropna(subset=[location_col, salary_col])

    result = (
        work.groupby(location_col, as_index=False)[salary_col]
        .mean()
        .rename(columns={salary_col: "avg_salary"})
        .sort_values("avg_salary", ascending=False)
    )
    return result

def count_jobs_by_country(df, country_col="country", job_col="job_title"):
    """Count job occurrences grouped by country from a query result."""
    if country_col not in df.columns or job_col not in df.columns:
        raise ValueError("DataFrame must include country and job_title columns")

    work = df[[country_col, job_col]].copy()
    work = work.dropna(subset=[country_col, job_col])

    result = (
        work.groupby(country_col, as_index=False)[job_col]
        .value_counts()
        .rename(columns={job_col: "job_count"})
        .sort_values("job_count", ascending=False)
    )
    return result

def highest_paying_job_by_location(df, location_col="location", job_col="job_title", salary_col="salary"):
    """Find the highest paying job for each location."""
    if location_col not in df.columns or job_col not in df.columns or salary_col not in df.columns:
        raise ValueError("DataFrame must include location, job_title, and salary columns")

    work = df[[location_col, job_col, salary_col]].copy()
    work[salary_col] = pd.to_numeric(work[salary_col], errors="coerce")
    work = work.dropna(subset=[location_col, job_col, salary_col])

    idx = work.groupby(location_col)[salary_col].idxmax()
    result = work.loc[idx].reset_index(drop=True)
    return result

def job_summary_by_location_in_country(conn, country):
    """Query detailed job summary (location, title, experience, count, avg_salary) for a country."""
    sql_template = get_query_by_label("queries.sql", "job summary by location in country")
    return pd.read_sql_query(sql_template, conn, params=[country])

def get_salaries_by_continent(conn, continent):
    """Query individual salary records for all jobs in a continent."""
    sql_template = get_query_by_label("queries.sql", "get salary by continent")
    return pd.read_sql_query(sql_template, conn, params=[continent])

def get_salaries_by_country(conn, country):
    """Query individual salary records for all jobs in a country."""
    sql_template = get_query_by_label("queries.sql", "get salary by country")
    return pd.read_sql_query(sql_template, conn, params=[country])