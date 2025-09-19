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


#----------------PDF FILE FUNCTIONS-----------------
def create_pdf(avg_salary, highest_salary, lowest_salary, median_salary):
    with PdfPages('salary_analysis.pdf') as pdf:
        fig, ax = plt.subplots(figsize=(8, 6))
        ax.axis('off')
        ax.text(0.5, 0.7, 'Salary Analysis Report', fontsize=24, ha='center')
        ax.text(0.05, 0.6, f"The following report will contain the main findings of the salary analysis.\n", fontsize=12, ha='left')
        ax.text(0.05, 0.55, '\nBasic Metrics:', fontsize=16, ha='center')
        ax.text(0.01, 0.5, f"Average salary: ${avg_salary['all_jobs']}", fontsize=12,ha='left')
        ax.text(0.01, 0.4, f"Highest salary: ${highest_salary['all_jobs']}", fontsize=12, ha='left')
        ax.text(0.01, 0.3, f"Lowest salary: ${lowest_salary['all_jobs']}", fontsize=12, ha='left')
        ax.text(0.01, 0.2, f"Median salary: ${median_salary['all_jobs']}", fontsize=12, ha='left')
        ax.text(0.05, 0.05, 'Job analysis: \n', fontsize=16, ha='center')
        ax.text(0.01, 0.0, 'DATA SCIENTIST:\n', fontsize=12, ha='left')
        ax.text(0.01, -0.05, f"Average salary: ${avg_salary}", fontsize=10, ha='left')
        ax.text(0.01,-0.1, f"Highest salary: ${highest_salary['data_scientist']}", fontsize=10, ha='left')
        ax.text(0.01,-0.15, f"Lowest salary: ${lowest_salary['data_scientist']}", fontsize=10, ha='left')
        pdf.savefig(fig)
        plt.close()
        
