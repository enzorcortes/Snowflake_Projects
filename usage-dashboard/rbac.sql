-- ============================================================
-- rbac.sql — Role-Based Access Control for the Usage Dashboard
-- Database: ECON_AGENT_DB  |  Schema: ANALYTICS
--
-- Three-tier role hierarchy:
--   USAGE_VIEWER  → dashboard-only access (no direct table queries)
--   USAGE_ANALYST → read-only on all tables + semantic view
--   USAGE_ADMIN   → full read/write on all tables
--
-- Hierarchy: VIEWER → ANALYST → ADMIN → ACCOUNTADMIN
-- Each role inherits everything from the role below it.
-- ============================================================

-- ------------------------------------------------------------
-- 1. Create roles
-- ------------------------------------------------------------
CREATE ROLE IF NOT EXISTS USAGE_VIEWER
  COMMENT = 'Can access the Streamlit dashboard but has no direct table access';

CREATE ROLE IF NOT EXISTS USAGE_ANALYST
  COMMENT = 'Read-only access to all usage tables and semantic view';

CREATE ROLE IF NOT EXISTS USAGE_ADMIN
  COMMENT = 'Full read/write access to usage tables, can manage semantic view';

-- ------------------------------------------------------------
-- 2. Build role hierarchy
--    VIEWER rolls into ANALYST, ANALYST rolls into ADMIN
-- ------------------------------------------------------------
GRANT ROLE USAGE_VIEWER  TO ROLE USAGE_ANALYST;
GRANT ROLE USAGE_ANALYST TO ROLE USAGE_ADMIN;
GRANT ROLE USAGE_ADMIN   TO ROLE ACCOUNTADMIN;

-- ------------------------------------------------------------
-- 3. Database and schema USAGE (granted at VIEWER level,
--    inherited by ANALYST and ADMIN automatically)
-- ------------------------------------------------------------
GRANT USAGE ON DATABASE ECON_AGENT_DB             TO ROLE USAGE_VIEWER;
GRANT USAGE ON SCHEMA   ECON_AGENT_DB.ANALYTICS   TO ROLE USAGE_VIEWER;

-- ------------------------------------------------------------
-- 4. Warehouse USAGE (granted at VIEWER level so all roles
--    can execute queries)
-- ------------------------------------------------------------
GRANT USAGE ON WAREHOUSE COMPUTE_WH TO ROLE USAGE_VIEWER;

-- ------------------------------------------------------------
-- 5. Table privileges — ANALYST (read-only)
--    SELECT on current and future tables so new tables are
--    automatically accessible without re-granting.
-- ------------------------------------------------------------
GRANT SELECT ON ALL TABLES    IN SCHEMA ECON_AGENT_DB.ANALYTICS TO ROLE USAGE_ANALYST;
GRANT SELECT ON FUTURE TABLES IN SCHEMA ECON_AGENT_DB.ANALYTICS TO ROLE USAGE_ANALYST;

-- ------------------------------------------------------------
-- 6. Table privileges — ADMIN (write access)
--    INSERT/UPDATE/DELETE on current and future tables.
--    ADMIN inherits SELECT from ANALYST via the hierarchy.
-- ------------------------------------------------------------
GRANT INSERT, UPDATE, DELETE ON ALL TABLES    IN SCHEMA ECON_AGENT_DB.ANALYTICS TO ROLE USAGE_ADMIN;
GRANT INSERT, UPDATE, DELETE ON FUTURE TABLES IN SCHEMA ECON_AGENT_DB.ANALYTICS TO ROLE USAGE_ADMIN;

-- ------------------------------------------------------------
-- 7. Semantic view — ANALYST (query via Cortex Analyst)
--    Semantic views use SELECT, not USAGE.
--    Also grant on future semantic views for new ones.
-- ------------------------------------------------------------
GRANT SELECT ON SEMANTIC VIEW ECON_AGENT_DB.ANALYTICS.USAGE_ANALYTICS_SV TO ROLE USAGE_ANALYST;
GRANT SELECT ON FUTURE SEMANTIC VIEWS IN SCHEMA ECON_AGENT_DB.ANALYTICS  TO ROLE USAGE_ANALYST;

-- ============================================================
-- Assign roles to users (uncomment and edit as needed)
-- ============================================================
-- GRANT ROLE USAGE_VIEWER  TO USER jane_doe;    -- dashboard only
-- GRANT ROLE USAGE_ANALYST TO USER john_smith;   -- read + Cortex Analyst
-- GRANT ROLE USAGE_ADMIN   TO USER team_lead;    -- full access

-- ============================================================
-- Verification queries (run these to confirm setup)
-- ============================================================
-- SHOW ROLES LIKE 'USAGE_%';
-- SHOW GRANTS TO ROLE USAGE_VIEWER;
-- SHOW GRANTS TO ROLE USAGE_ANALYST;
-- SHOW GRANTS TO ROLE USAGE_ADMIN;
