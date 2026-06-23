--jobs by location
SELECT {location} AS location, COUNT(*) AS job_count
FROM salaries
WHERE {location} IS NOT NULL
GROUP BY {location}
ORDER BY job_count DESC, {location};

--jobs by country in continent
SELECT country AS location, COUNT(*) AS job_count
FROM salaries
WHERE continent = ?
  AND country IS NOT NULL
GROUP BY country
ORDER BY job_count DESC, country;

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
SELECT DISTINCT continent
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

--job summary by location in country
SELECT
  location,
  job_title,
  experience_level,
  COUNT(*) AS job_count,
  Round (AVG(salary),2) AS avg_salary
FROM salaries
WHERE country = ?
  AND country IS NOT NULL
  AND location IS NOT NULL
  AND job_title IS NOT NULL
  AND experience_level IS NOT NULL
  AND salary IS NOT NULL
GROUP BY location, job_title, experience_level
ORDER BY location, job_title, experience_level;

--get salary by continent
SELECT country, location, job_title, experience_level, salary
FROM salaries
WHERE continent = ? AND salary IS NOT NULL
ORDER BY salary DESC

--get salary by country
    SELECT location, job_title, experience_level, salary
    FROM salaries
    WHERE country = ? AND salary IS NOT NULL
    ORDER BY salary DESC
