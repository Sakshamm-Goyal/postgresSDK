/*
 * File: extract_database.sql
 * Purpose: Extracts list of databases from PostgreSQL server
 *
 * Description:
 *   - Retrieves all non-system databases from pg_database
 *   - Excludes system databases (template0, template1, postgres)
 *   - Includes database size and connection count information
 *   - Enhanced with business context and metadata
 */

SELECT 
    d.datname AS database_name,
    pg_size_pretty(pg_database_size(d.datname)) AS database_size,
    d.datcollate AS collation,
    d.datctype AS character_type,
    d.datconnlimit AS connection_limit,
    CASE 
        WHEN d.datconnlimit = -1 THEN 'Unlimited'
        ELSE d.datconnlimit::text
    END AS connection_limit_display,
    d.datallowconn AS allows_connections,
    d.datistemplate AS is_template,
    d.datacl AS access_privileges,
    pg_database_size(d.datname) AS size_bytes,
    (SELECT COUNT(*) FROM pg_stat_activity WHERE datname = d.datname) AS active_connections
FROM pg_database d
WHERE d.datname NOT IN ('template0', 'template1', 'postgres')
    AND d.datistemplate = false
ORDER BY d.datname;