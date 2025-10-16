import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages

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

def get_query_by_location(filename, label, column):
    # TODO: Implement this function
    pass
    

#delete double entries based on all columns
def remove_duplicates(df):
    return df.drop_duplicates()

#update db with new dataframe
def update_database(df, conn, table_name):
    df.to_sql(table_name, conn, if_exists='replace', index=False)
    conn.commit()


#-----------------FILE FUNCTIONS-----------------

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

#bar chart for job distribution by location
def bar_distribution_by_location(df, location):
    fig,ax = plt.subplots(figsize=(8.5, 5.5))
    filtered_df = df[df['continent'] == location]
    ax.bar(filtered_df['salary'], filtered_df['count'], color='skyblue')
    ax.set_xlabel('Salary')
    ax.set_ylabel('Count')
    ax.set_title(f'Salary Distribution for {location}')
    plt.show()
