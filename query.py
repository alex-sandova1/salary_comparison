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

#Quiery continent list
def get_continents(conn):
    sql_template = get_query_by_label("queries.sql", "continent list")
    return pd.read_sql_query(sql_template, conn)