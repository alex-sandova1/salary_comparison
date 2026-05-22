--jobs by location
SELECT {location} AS location, COUNT(*) AS job_count
FROM salaries
WHERE {location} IS NOT NULL
GROUP BY {location}
ORDER BY job_count DESC;

--jobs by country in continent
SELECT country AS location, COUNT(*) AS job_count
FROM salaries
WHERE continent = ?
    AND country IS NOT NULL
GROUP BY country
ORDER BY job_count DESC;

--continent list
SELECT DISTINCT continent
FROM salaries
WHERE continent IS NOT NULL
ORDER BY continent;