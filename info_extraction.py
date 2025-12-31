from utils import get_database_connection, clean_text
from queries import fetch_salary_data, fetch_job_titles

def gather_info():
    # Establish database connection
    conn = get_database_connection()
    
    # Fetch salary data and job titles
    salary_data = fetch_salary_data(conn)
    job_titles = fetch_job_titles(conn)
    
    # Clean and process data
    cleaned_salary_data = [clean_text(record) for record in salary_data]
    cleaned_job_titles = [clean_text(title) for title in job_titles]
    
    # Combine and return info
    info = {
        "salaries": cleaned_salary_data,
        "job_titles": cleaned_job_titles
    }
    return info

if __name__ == "__main__":
    info = gather_info()
    print(info)