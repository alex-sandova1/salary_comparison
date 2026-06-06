--jobs by continent
SELECT continent, country, job_title, experience_level
FROM salaries
WHERE continent = ?
  AND continent IS NOT NULL
ORDER BY country, job_title, experience_level;

--job by country
SELECT country,location ,job_title, experience_level, Salary
FROM salaries
WHERE country = ?
  AND country IS NOT NULL
ORDER BY country, job_title, experience_level;

--job by location
SELECT location, job_title, experience_level, Salary
FROM salaries
WHERE location = ?
  AND location IS NOT NULL
ORDER BY location, job_title, experience_level;

--continent list
SELECT continent
FROM salaries
WHERE continent IS NOT NULL
ORDER BY continent;

--job titles by location
SELECT DISTINCT country AS location, job_title, experience_level, salary
FROM salaries
WHERE continent = ?
  AND country IS NOT NULL
  AND job_title IS NOT NULL
ORDER BY country, job_title;