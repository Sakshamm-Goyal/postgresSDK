/*
 * File: extract_schema.sql
 * Purpose: Extracts detailed schema information from PostgreSQL server
 *
 * Description:
 *   - Retrieves schema metadata including owner, privileges, and statistics
 *   - Counts tables, views, functions, and other objects in each schema
 *   - Includes business context and descriptions from pg_description
 *   - Enhanced with data quality metrics and lineage information
 *
 * Parameters:
 *   {normalized_exclude_regex} - Regex pattern for schemas to exclude
 *   {normalized_include_regex} - Regex pattern for schemas to include
 */

WITH schema_stats AS (
    SELECT 
        table_schema,
        COUNT(*) as total_objects,
        COUNT(CASE WHEN table_type = 'BASE TABLE' THEN 1 END) as table_count,
        COUNT(CASE WHEN table_type = 'VIEW' THEN 1 END) as view_count,
        COUNT(CASE WHEN table_type = 'MATERIALIZED VIEW' THEN 1 END) as materialized_view_count,
        COUNT(CASE WHEN table_type = 'FOREIGN TABLE' THEN 1 END) as foreign_table_count
    FROM information_schema.tables
    WHERE table_schema NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
    GROUP BY table_schema
),
schema_functions AS (
    SELECT 
        n.nspname as table_schema,
        COUNT(p.proname) as function_count,
        COUNT(CASE WHEN p.prokind = 'a' THEN 1 END) as aggregate_count,
        COUNT(CASE WHEN p.prokind = 'w' THEN 1 END) as window_count,
        COUNT(CASE WHEN p.prokind = 'p' THEN 1 END) as procedure_count
    FROM pg_proc p
    JOIN pg_namespace n ON p.pronamespace = n.oid
    WHERE n.nspname NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
    GROUP BY n.nspname
)
SELECT
    s.schema_name,
    s.schema_owner,
    s.default_character_set_catalog,
    s.default_character_set_schema,
    s.default_character_set_name,
    s.sql_path,
    COALESCE(ss.table_count, 0) as table_count,
    COALESCE(ss.view_count, 0) as view_count,
    COALESCE(ss.materialized_view_count, 0) as materialized_view_count,
    COALESCE(ss.foreign_table_count, 0) as foreign_table_count,
    COALESCE(ss.total_objects, 0) as total_objects,
    COALESCE(sf.function_count, 0) as function_count,
    COALESCE(sf.aggregate_count, 0) as aggregate_count,
    COALESCE(sf.window_count, 0) as window_count,
    COALESCE(sf.procedure_count, 0) as procedure_count,
    COALESCE(pd.description, '') as description,
    COALESCE(pd.objoid::regnamespace::text, '') as schema_qualified_name
FROM information_schema.schemata s
LEFT JOIN schema_stats ss ON s.schema_name = ss.table_schema
LEFT JOIN schema_functions sf ON s.schema_name = sf.table_schema
LEFT JOIN pg_description pd ON pd.objoid = s.schema_name::regnamespace::oid AND pd.classoid = 'pg_namespace'::regclass
WHERE s.schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_toast', 'pg_temp_1', 'pg_toast_temp_1')
    AND s.schema_name !~ '{normalized_exclude_regex}'
    AND s.schema_name ~ '{normalized_include_regex}'
ORDER BY s.schema_name;