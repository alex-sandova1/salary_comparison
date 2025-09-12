#-----------------DATAFRAME FUNCTIONS-----------------

#Extract a specific query from the SQL file using a label
def get_query_by_label(filename, label):
    with open(filename, 'r') as f:
        content = f.read()
    # Split by comment lines
    queries = content.split('--')
    for q in queries:
        lines = q.strip().splitlines()
        if not lines:
            continue
        comment = lines[0].strip().lower()
        sql = '\n'.join(lines[1:]).strip()
        if label.lower() in comment and sql:
            # Remove trailing semicolon if present
            if sql.endswith(';'):
                sql = sql[:-1]
            return sql
    return None

#delete double entries based on all columns
def remove_duplicates(df):
    return df.drop_duplicates()


#-----------------GRAPH FUNCTIONS-----------------

#graph salary distribution
def plot_salary_distribution(df):
    import matplotlib.pyplot as plt
    df['salary'].hist()
    plt.xlabel('Salary')
    plt.ylabel('Count')
    plt.title('Salary Distribution')
    plt.show()

#graph salary distribution by job title
def plot_salary_distribution_by_title(df, title):
    import matplotlib.pyplot as plt
    filtered_df = df[df['job_title'] == title]
    filtered_df['salary'].hist()
    plt.xlabel('Salary')
    plt.ylabel('Count')
    plt.title(f'Salary Distribution for {title}')
    plt.show()