-- ============================================================
-- setup.sql — Schema + seed data for the Usage Dashboard
-- Database: ECON_AGENT_DB  |  Schema: ANALYTICS
-- Run this file once to (re)create all tables and populate
-- them with 12 months of synthetic usage data.
-- ============================================================

USE DATABASE ECON_AGENT_DB;
USE SCHEMA ANALYTICS;

-- ------------------------------------------------------------
-- 1. TEAMS  (5 teams)
-- ------------------------------------------------------------
CREATE OR REPLACE TABLE TEAMS (
    TEAM_ID       INT,
    TEAM_NAME     VARCHAR(50),
    DEPARTMENT    VARCHAR(50),
    COST_CENTER   VARCHAR(20),
    MANAGER_NAME  VARCHAR(100)
);

INSERT INTO TEAMS VALUES
(1, 'Data Engineering',    'Engineering',      'ENG-001', 'Sarah Chen'),
(2, 'Machine Learning',    'Engineering',      'ENG-002', 'Marcus Johnson'),
(3, 'Analytics',           'Business Ops',     'BIZ-001', 'Priya Patel'),
(4, 'Platform Ops',        'Infrastructure',   'INF-001', 'David Kim'),
(5, 'Product Development', 'Engineering',      'ENG-003', 'Elena Rodriguez');

-- ------------------------------------------------------------
-- 2. SERVICES  (10 cloud services with cost-per-unit rates)
-- ------------------------------------------------------------
CREATE OR REPLACE TABLE SERVICES (
    SERVICE_ID        INT,
    SERVICE_NAME      VARCHAR(100),
    SERVICE_CATEGORY  VARCHAR(50),
    UNIT              VARCHAR(30),
    COST_PER_UNIT     FLOAT,
    DESCRIPTION       VARCHAR(200)
);

INSERT INTO SERVICES VALUES
(1,  'Snowflake Compute',   'Compute',    'credits',    3.00,  'Virtual warehouse compute credits'),
(2,  'Snowflake Storage',   'Storage',    'TB/month',  23.00,  'Managed data storage'),
(3,  'Cortex AI Functions', 'AI/ML',      'tokens',     0.012, 'LLM inference and AI functions'),
(4,  'Snowpark Compute',    'Compute',    'credits',    3.50,  'Snowpark container runtime'),
(5,  'Data Transfer',       'Networking', 'TB',          9.00,  'Cross-region data transfer'),
(6,  'Cortex Search',       'AI/ML',      'queries',     0.005, 'Vector search service'),
(7,  'Replication',         'Storage',    'credits',     2.50,  'Database replication'),
(8,  'Serverless Tasks',    'Compute',    'credits',     3.00,  'Serverless task execution'),
(9,  'Materialized Views',  'Compute',    'credits',     3.00,  'Automatic MV maintenance'),
(10, 'Cortex Analyst',      'AI/ML',      'queries',     0.02,  'Natural language analytics');

-- ------------------------------------------------------------
-- 3. EMPLOYEES  (100 people, 20 per team, 5 seniority levels)
-- ------------------------------------------------------------
CREATE OR REPLACE TABLE EMPLOYEES (
    EMPLOYEE_ID  INT,
    FULL_NAME    VARCHAR(100),
    EMAIL        VARCHAR(150),
    TEAM_ID      INT,
    ROLE_TITLE   VARCHAR(80),
    SENIORITY    VARCHAR(20),
    HIRE_DATE    DATE,
    IS_ACTIVE    BOOLEAN
);

INSERT INTO EMPLOYEES
WITH
names AS (
    SELECT column1 AS full_name, ROW_NUMBER() OVER (ORDER BY column1) AS rn FROM VALUES
    ('James Smith'),('Mary Johnson'),('Robert Williams'),('Patricia Brown'),('John Jones'),
    ('Jennifer Garcia'),('Michael Miller'),('Linda Davis'),('David Rodriguez'),('Elizabeth Martinez'),
    ('William Hernandez'),('Barbara Lopez'),('Richard Gonzalez'),('Susan Wilson'),('Joseph Anderson'),
    ('Jessica Thomas'),('Thomas Taylor'),('Sarah Moore'),('Christopher Jackson'),('Karen Martin'),
    ('Charles Lee'),('Lisa Perez'),('Daniel Thompson'),('Nancy White'),('Matthew Harris'),
    ('Betty Sanchez'),('Anthony Clark'),('Margaret Ramirez'),('Mark Lewis'),('Sandra Robinson'),
    ('Andrew Walker'),('Ashley Young'),('Steven Allen'),('Dorothy King'),('Paul Wright'),
    ('Kimberly Scott'),('Joshua Torres'),('Emily Nguyen'),('Kenneth Hill'),('Donna Flores'),
    ('Kevin Green'),('Michelle Adams'),('Brian Nelson'),('Carol Baker'),('George Hall'),
    ('Amanda Rivera'),('Timothy Campbell'),('Melissa Mitchell'),('Ronald Carter'),('Deborah Roberts'),
    ('Jason Reed'),('Stephanie Cook'),('Ryan Morgan'),('Nicole Bell'),('Jacob Murphy'),
    ('Heather Bailey'),('Gary Rivera'),('Samantha Cooper'),('Eric Richardson'),('Rachel Cox'),
    ('Stephen Howard'),('Laura Ward'),('Larry Torres'),('Megan Peterson'),('Justin Gray'),
    ('Hannah Ramirez'),('Brandon James'),('Amber Watson'),('Samuel Brooks'),('Danielle Kelly'),
    ('Benjamin Sanders'),('Brittany Price'),('Gregory Bennett'),('Katherine Wood'),('Alexander Barnes'),
    ('Natalie Ross'),('Patrick Henderson'),('Vanessa Coleman'),('Frank Jenkins'),('Courtney Perry'),
    ('Raymond Powell'),('Christina Long'),('Jack Patterson'),('Sara Hughes'),('Dennis Flores'),
    ('Tracy Washington'),('Jerry Butler'),('Catherine Simmons'),('Tyler Foster'),('Kayla Gonzales'),
    ('Aaron Bryant'),('Maria Alexander'),('Jose Russell'),('Andrea Griffin'),('Nathan Diaz'),
    ('Tiffany Hayes'),('Henry Myers'),('Lauren Ford'),('Peter Hamilton'),('Julie Graham')
),
roles AS (
    SELECT column1 AS team_id, column2 AS role_title, column3 AS seniority, column4 AS role_idx FROM VALUES
    (1,'Data Engineer','Junior',1),(1,'Data Engineer','Mid',2),(1,'Senior Data Engineer','Senior',3),(1,'Staff Data Engineer','Staff',4),(1,'Data Engineering Lead','Lead',5),
    (2,'ML Engineer','Junior',1),(2,'ML Engineer','Mid',2),(2,'Senior ML Engineer','Senior',3),(2,'ML Scientist','Staff',4),(2,'ML Engineering Lead','Lead',5),
    (3,'Data Analyst','Junior',1),(3,'Data Analyst','Mid',2),(3,'Senior Analyst','Senior',3),(3,'Analytics Engineer','Staff',4),(3,'Analytics Lead','Lead',5),
    (4,'DevOps Engineer','Junior',1),(4,'DevOps Engineer','Mid',2),(4,'Senior DevOps','Senior',3),(4,'SRE','Staff',4),(4,'Platform Lead','Lead',5),
    (5,'Software Engineer','Junior',1),(5,'Software Engineer','Mid',2),(5,'Senior SWE','Senior',3),(5,'Staff SWE','Staff',4),(5,'Engineering Lead','Lead',5)
)
SELECT
    n.rn AS employee_id,
    n.full_name,
    LOWER(REPLACE(n.full_name, ' ', '.')) || '@acmecorp.com' AS email,
    MOD(n.rn - 1, 5) + 1 AS team_id,
    r.role_title,
    r.seniority,
    DATEADD('day', -1 * (UNIFORM(90, 1800, RANDOM())), '2025-09-01'::DATE) AS hire_date,
    TRUE AS is_active
FROM names n
JOIN roles r ON r.team_id = MOD(n.rn - 1, 5) + 1
            AND r.role_idx = MOD(FLOOR((n.rn - 1) / 5), 5) + 1;

-- ------------------------------------------------------------
-- 4. DAILY_USAGE  (~116k rows, Sep 2024 – Aug 2025)
--    Patterns: team-service affinity, seniority scaling,
--    weekday/weekend, monthly growth, random noise, ~2% spikes
-- ------------------------------------------------------------
CREATE OR REPLACE TABLE DAILY_USAGE (
    USAGE_ID       INT AUTOINCREMENT,
    EMPLOYEE_ID    INT,
    SERVICE_ID     INT,
    USAGE_DATE     DATE,
    UNITS_CONSUMED FLOAT,
    COST_USD       FLOAT,
    SESSION_COUNT  INT,
    QUERY_COUNT    INT,
    IS_SPIKE       BOOLEAN
);

INSERT INTO DAILY_USAGE (EMPLOYEE_ID, SERVICE_ID, USAGE_DATE, UNITS_CONSUMED, COST_USD, SESSION_COUNT, QUERY_COUNT, IS_SPIKE)
WITH
date_spine AS (
    SELECT DATEADD('day', SEQ4(), '2024-09-01'::DATE) AS dt
    FROM TABLE(GENERATOR(ROWCOUNT => 365))
    WHERE DATEADD('day', SEQ4(), '2024-09-01'::DATE) <= '2025-08-31'
),
team_service_affinity AS (
    SELECT column1 AS team_id, column2 AS service_id, column3 AS weight FROM VALUES
    (1,1,3.0),(1,2,2.0),(1,8,2.5),(1,5,1.5),(1,7,1.0),
    (2,3,4.0),(2,4,3.0),(2,6,2.5),(2,1,1.5),(2,10,1.0),
    (3,1,2.0),(3,10,3.5),(3,2,1.5),(3,3,1.0),(3,9,1.5),
    (4,1,2.5),(4,7,3.0),(4,8,2.5),(4,5,2.0),(4,2,1.5),
    (5,4,3.0),(5,1,2.0),(5,3,1.5),(5,6,1.0),(5,5,1.0)
),
seniority_mult AS (
    SELECT column1 AS seniority, column2 AS mult FROM VALUES
    ('Junior',0.4),('Mid',0.7),('Senior',1.2),('Staff',1.8),('Lead',1.5)
),
base_usage AS (
    SELECT
        e.EMPLOYEE_ID,
        ts.service_id,
        d.dt AS usage_date,
        ts.weight,
        sm.mult AS seniority_mult,
        CASE WHEN DAYOFWEEK(d.dt) IN (0, 6) THEN 0.15 ELSE 1.0 END AS dow_factor,
        1.0 + (DATEDIFF('month', '2024-09-01', d.dt) * 0.03) AS growth_factor,
        UNIFORM(0.3, 1.7, RANDOM()) AS daily_noise,
        CASE WHEN UNIFORM(0, 100, RANDOM()) < 2 THEN UNIFORM(3.0, 8.0, RANDOM()) ELSE 1.0 END AS spike_mult
    FROM EMPLOYEES e
    JOIN team_service_affinity ts ON ts.team_id = e.TEAM_ID
    JOIN seniority_mult sm ON sm.seniority = e.SENIORITY
    CROSS JOIN date_spine d
    WHERE UNIFORM(0, 100, RANDOM()) < (40 + ts.weight * 12)
)
SELECT
    EMPLOYEE_ID,
    service_id,
    usage_date,
    ROUND(weight * seniority_mult * dow_factor * growth_factor * daily_noise * spike_mult *
          CASE service_id
              WHEN 1 THEN UNIFORM(5, 40, RANDOM())
              WHEN 2 THEN UNIFORM(0.1, 2.0, RANDOM())
              WHEN 3 THEN UNIFORM(500, 15000, RANDOM())
              WHEN 4 THEN UNIFORM(3, 25, RANDOM())
              WHEN 5 THEN UNIFORM(0.05, 1.0, RANDOM())
              WHEN 6 THEN UNIFORM(100, 5000, RANDOM())
              WHEN 7 THEN UNIFORM(2, 15, RANDOM())
              WHEN 8 THEN UNIFORM(1, 20, RANDOM())
              WHEN 9 THEN UNIFORM(2, 12, RANDOM())
              WHEN 10 THEN UNIFORM(50, 2000, RANDOM())
          END, 2) AS units_consumed,
    0 AS cost_usd,
    GREATEST(1, ROUND(UNIFORM(1, 8, RANDOM()) * seniority_mult * dow_factor)) AS session_count,
    GREATEST(1, ROUND(UNIFORM(5, 200, RANDOM()) * seniority_mult * dow_factor)) AS query_count,
    CASE WHEN spike_mult > 1.0 THEN TRUE ELSE FALSE END AS is_spike
FROM base_usage;

-- Backfill COST_USD from service rates
UPDATE DAILY_USAGE u
SET COST_USD = ROUND(u.UNITS_CONSUMED * s.COST_PER_UNIT, 2)
FROM SERVICES s
WHERE u.SERVICE_ID = s.SERVICE_ID;

-- ------------------------------------------------------------
-- 5. USAGE_ALERTS  (spike events with severity + resolution)
-- ------------------------------------------------------------
CREATE OR REPLACE TABLE USAGE_ALERTS (
    ALERT_ID         INT AUTOINCREMENT,
    EMPLOYEE_ID      INT,
    SERVICE_ID       INT,
    ALERT_DATE       DATE,
    ALERT_TYPE       VARCHAR(50),
    SEVERITY         VARCHAR(20),
    NORMAL_AVG_COST  FLOAT,
    SPIKE_COST       FLOAT,
    MULTIPLIER       FLOAT,
    RESOLVED         BOOLEAN,
    RESOLUTION_NOTES VARCHAR(300)
);

INSERT INTO USAGE_ALERTS (EMPLOYEE_ID, SERVICE_ID, ALERT_DATE, ALERT_TYPE, SEVERITY,
                          NORMAL_AVG_COST, SPIKE_COST, MULTIPLIER, RESOLVED, RESOLUTION_NOTES)
WITH spike_days AS (
    SELECT
        EMPLOYEE_ID, SERVICE_ID, USAGE_DATE, COST_USD,
        AVG(COST_USD) OVER (PARTITION BY EMPLOYEE_ID, SERVICE_ID
                            ORDER BY USAGE_DATE ROWS BETWEEN 30 PRECEDING AND 1 PRECEDING) AS avg_30d
    FROM DAILY_USAGE
    WHERE IS_SPIKE = TRUE
)
SELECT
    EMPLOYEE_ID,
    SERVICE_ID,
    USAGE_DATE,
    CASE
        WHEN COST_USD / NULLIF(avg_30d, 0) > 5 THEN 'EXTREME_SPIKE'
        WHEN COST_USD / NULLIF(avg_30d, 0) > 3 THEN 'HIGH_SPIKE'
        ELSE 'MODERATE_SPIKE'
    END,
    CASE
        WHEN COST_USD / NULLIF(avg_30d, 0) > 5 THEN 'CRITICAL'
        WHEN COST_USD / NULLIF(avg_30d, 0) > 3 THEN 'HIGH'
        ELSE 'MEDIUM'
    END,
    ROUND(avg_30d, 2),
    ROUND(COST_USD, 2),
    ROUND(COST_USD / NULLIF(avg_30d, 0), 1),
    CASE WHEN UNIFORM(0,100,RANDOM()) < 80 THEN TRUE ELSE FALSE END,
    CASE WHEN UNIFORM(0,100,RANDOM()) < 40 THEN 'Batch job overrun - schedule adjusted'
         WHEN UNIFORM(0,100,RANDOM()) < 60 THEN 'ML training pipeline spike - expected'
         WHEN UNIFORM(0,100,RANDOM()) < 80 THEN 'Data backfill completed'
         ELSE 'Under investigation'
    END
FROM spike_days
WHERE avg_30d > 0;

-- ------------------------------------------------------------
-- 6. MONTHLY_BUDGET  (budget per team per month, 5-25% above actual)
-- ------------------------------------------------------------
CREATE OR REPLACE TABLE MONTHLY_BUDGET (
    BUDGET_ID      INT AUTOINCREMENT,
    TEAM_ID        INT,
    BUDGET_MONTH   DATE,
    BUDGET_AMOUNT  FLOAT,
    ACTUAL_SPEND   FLOAT
);

INSERT INTO MONTHLY_BUDGET (TEAM_ID, BUDGET_MONTH, BUDGET_AMOUNT, ACTUAL_SPEND)
WITH actual AS (
    SELECT
        e.TEAM_ID,
        DATE_TRUNC('month', u.USAGE_DATE) AS mo,
        SUM(u.COST_USD) AS total_spend
    FROM DAILY_USAGE u
    JOIN EMPLOYEES e ON u.EMPLOYEE_ID = e.EMPLOYEE_ID
    GROUP BY 1, 2
)
SELECT
    TEAM_ID,
    mo,
    ROUND(total_spend * UNIFORM(1.05, 1.25, RANDOM()), 2) AS budget,
    ROUND(total_spend, 2) AS actual
FROM actual;

-- ============================================================
-- Verification
-- ============================================================
SELECT 'TEAMS' AS tbl, COUNT(*) AS cnt FROM TEAMS
UNION ALL SELECT 'EMPLOYEES', COUNT(*) FROM EMPLOYEES
UNION ALL SELECT 'SERVICES', COUNT(*) FROM SERVICES
UNION ALL SELECT 'DAILY_USAGE', COUNT(*) FROM DAILY_USAGE
UNION ALL SELECT 'USAGE_ALERTS', COUNT(*) FROM USAGE_ALERTS
UNION ALL SELECT 'MONTHLY_BUDGET', COUNT(*) FROM MONTHLY_BUDGET;
