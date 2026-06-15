import pandas as pd


# Extract a specific query from the SQL file using a label
def get_query_by_label(filename, label):
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


# Delete duplicate rows based on all columns
def remove_duplicates(df):
    return df.drop_duplicates()


# Update database with dataframe
def update_database(df, conn, table_name):
    df.to_sql(table_name, conn, if_exists="replace", index=False)
    conn.commit()


# Query jobs grouped by continent
def group_location(conn, location):
    location_key = location.strip().lower()
    if location_key not in {"continent", "country", "location"}:
        raise ValueError("location must be one of: continent, country, location")

    sql_template = get_query_by_label("queries.sql", "jobs by location")
    sql = sql_template.format(location=location_key)
    return pd.read_sql_query(sql, conn)

#query jobs grouped by country within a continent
def group_country(conn, continent):
    sql_template = get_query_by_label("queries.sql", "jobs by country in continent")
    return pd.read_sql_query(sql_template, conn, params=[continent])

# Query jobs grouped by continent
def count_jobs_by_country_in_continent(conn, continent):
    return group_country(conn, continent)

#Query continent list
def get_continents(conn):
    sql_template = get_query_by_label("queries.sql", "continent list")
    return pd.read_sql_query(sql_template, conn)

#Query to get job titles by continent
def jobs_by_continent(conn, continent):
    get_query_template = get_query_by_label("queries.sql", "jobs by continent")
    return pd.read_sql_query(get_query_template, conn, params=[continent])

#Query to get job titles by country
def jobs_by_country(conn, country):
    get_query_template = get_query_by_label("queries.sql", "job by country")
    return pd.read_sql_query(get_query_template, conn, params=[country])

#Query to get job titles by location (states, cities, etc.)
def jobs_by_location(conn, location):
    get_query_template = get_query_by_label("queries.sql", "job by location")
    return pd.read_sql_query(get_query_template, conn, params=[location])

#finds the average salary by location using the jobs_by_location query result as input
def avg_salary_by_location(df, location_col="location", salary_col="salary"):
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

#find how many of each job based on experience level in continent using the group_country query result as input
def count_jobs_by_country(df, country_col="country", job_col="job_title"):
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

#get highest paying job by location using the jobs_by_location query result as input
def highest_paying_job_by_location(df, location_col="location", job_col="job_title", salary_col="salary"):
    if location_col not in df.columns or job_col not in df.columns or salary_col not in df.columns:
        raise ValueError("DataFrame must include location, job_title, and salary columns")

    work = df[[location_col, job_col, salary_col]].copy()
    work[salary_col] = pd.to_numeric(work[salary_col], errors="coerce")
    work = work.dropna(subset=[location_col, job_col, salary_col])

    idx = work.groupby(location_col)[salary_col].idxmax()
    result = work.loc[idx].reset_index(drop=True)
    return result

def job_summary_by_location_in_country(conn, country):
    sql_template = get_query_by_label("queries.sql", "job summary by location in country")
    return pd.read_sql_query(sql_template, conn, params=[country])