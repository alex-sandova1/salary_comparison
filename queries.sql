-- Query to get average salary for all scientists

SELECT AVG(salary) AS average_salary 
FROM salaries

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

