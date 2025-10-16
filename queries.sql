-- average salary
SELECT AVG(salary) AS average_salary 
FROM salaries;

--average salary by job title
SELECT job_title, AVG(salary) AS average_salary
FROM salaries
GROUP BY job_title;

--amount of each job title
SELECT job_title, COUNT(*) 
AS count 
FROM salaries 
GROUP BY job_title;

--highest salary
SELECT * 
FROM salaries 
ORDER BY salary 
DESC LIMIT 1;

--lowest salary
SELECT * 
FROM salaries 
ORDER BY salary 
ASC LIMIT 1;


--number of employees per job title
SELECT job_title, COUNT(*) AS count
FROM salaries
GROUP BY job_title;

--median salary
SELECT AVG(salary) AS median_salary
FROM (
    SELECT salary
    FROM salaries
    ORDER BY salary
    LIMIT 2 - (SELECT COUNT(*) FROM salaries) % 2
    OFFSET (SELECT (COUNT(*) - 1) / 2 FROM salaries)
) AS median_subquery;

--jobs based on location except remote
SELECT location, COUNT(*) AS count
FROM salaries
WHERE location NOT LIKE '%Remote%' AND location NOT LIKE '%work%' 
GROUP BY location;

--remote jobs
SELECT COUNT(*) AS remote_job_count
FROM salaries
WHERE location = 'Remote';

--jobs based on country
SELECT country, COUNT(*) AS count
FROM salaries
WHERE country IS NOT NULL AND country != 'N/A'
GROUP BY country;

--jobs based on continent
SELECT continent, COUNT(*) AS count
FROM salaries
WHERE continent IS NOT NULL AND continent != 'N/A'
GROUP BY continent;

--jobs based on country on a specific location
SELECT continent, country, location, COUNT(*) AS job_count
FROM salaries
WHERE continent = ? OR country = ? OR location = ?
GROUP BY continent, country, location;

--experience level distribution  grouped by country then experience level
SELECT country, experience_level, COUNT(*) AS count
FROM salaries
GROUP BY country, experience_level;

--average pay by job based on experience level
SELECT job_title, experience_level, AVG(salary) AS average_salary
FROM salaries
GROUP BY job_title, experience_level;

--count of job salary based on experience level and job title
SELECT job_title, experience_level, COUNT(*) AS count
FROM salaries
GROUP BY job_title, experience_level;

--max salary by job title
SELECT job_title, MAX(salary) AS max_salary
FROM salaries
GROUP BY job_title;

--lowest salary by job title
SELECT job_title, MIN(salary) AS min_salary
FROM salaries
GROUP BY job_title;

--max salary by job title and experience level
SELECT job_title, experience_level, MAX(salary) AS max_salary
FROM salaries
GROUP BY job_title, experience_level;

--min salary by job title and experience level
SELECT job_title, experience_level, MIN(salary) AS min_salary
FROM salaries
GROUP BY job_title, experience_level;

--average salary by job title and experience level
SELECT job_title, experience_level, AVG(salary) AS average_salary
FROM salaries
GROUP BY job_title, experience_level;