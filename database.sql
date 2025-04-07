CREATE TABLE IF NOT EXISTS urls (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    name VARCHAR(255) NOT NULL UNIQUE,
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS url_checks (
    id BIGINT PRIMARY KEY GENERATED ALWAYS AS IDENTITY,
    url_id BIGINT REFERENCES urls(id),
    status_code INT,
    h1 VARCHAR(255),
    title VARCHAR(255),
    description VARCHAR(255),
    created_at TIMESTAMP NOT NULL DEFAULT CURRENT_TIMESTAMP
);

WITH last_checks_url AS (
    SELECT 
        url_id, 
        MAX(created_at) AS created_at
    FROM url_checks 
    GROUP BY url_id
),
last_check AS (
    SELECT 
        url_checks.status_code,
        last_checks_url.url_id,
        last_checks_url.created_at
        FROM last_checks_url 
            INNER JOIN url_checks
            ON last_checks_url.url_id = url_checks.url_id 
                AND last_checks_url.created_at = url_checks.created_at
)

SELECT 
    urls.name,
    urls.id,
    last_check.status_code,
    last_check.created_at
FROM urls LEFT JOIN last_check ON urls.id = last_check.url_id
ORDER BY  last_check.created_at DESC NULLS LAST, urls.created_at DESC;

SELECT * FROM last_check;



SELECT 
    urls.id,
    urls.name,
    last_checks,
