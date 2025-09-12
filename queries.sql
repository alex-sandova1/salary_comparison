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

--highest salary by job title
SELECT job_title, MAX(salary) AS highest_salary
FROM salaries
GROUP BY job_title;

--lowest salary
SELECT * 
FROM salaries 
ORDER BY salary 
ASC LIMIT 1;

--lowest salary by job title
SELECT job_title, MIN(salary) AS lowest_salary
FROM salaries
GROUP BY job_title;

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