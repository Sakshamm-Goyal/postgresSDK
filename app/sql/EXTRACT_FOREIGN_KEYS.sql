/*
 * File: extract_foreign_keys.sql
 * Purpose: Extracts foreign key relationships and lineage information
 *
 * Description:
 *   - Retrieves comprehensive foreign key relationships between tables
 *   - Includes constraint details, update/delete rules, and column mappings
 *   - Enhanced with business context and relationship metadata
 *   - Provides lineage information for data governance
 *
 * Parameters:
 *   {normalized_exclude_regex} - Regex pattern for schemas to exclude
 *   {normalized_include_regex} - Regex pattern for schemas to include
 *   {temp_table_regex_sql} - SQL fragment for additional table filtering
 */

SELECT
    tc.table_catalog AS database_name,
    tc.table_schema AS source_schema,
    tc.table_name AS source_table,
    kcu.column_name AS source_column,
    ccu.table_schema AS target_schema,
    ccu.table_name AS target_table,
    ccu.column_name AS target_column,
    tc.constraint_name,
    rc.update_rule,
    rc.delete_rule,
    tc.is_deferrable,
    tc.initially_deferred,
    pg_get_constraintdef(c.oid) AS constraint_definition,
    c.convalidated AS is_validated,
    c.connoinherit AS is_no_inherit,
    d.description AS constraint_description,
    kcu.ordinal_position AS column_position
FROM
    information_schema.table_constraints tc
JOIN
    information_schema.key_column_usage kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
JOIN
    information_schema.constraint_column_usage ccu
    ON tc.constraint_name = ccu.constraint_name
    AND tc.table_schema = ccu.table_schema
JOIN
    information_schema.referential_constraints rc
    ON tc.constraint_name = rc.constraint_name
    AND tc.table_schema = rc.constraint_schema
JOIN
    pg_constraint c
    ON c.conname = tc.constraint_name
    AND c.connamespace = (SELECT oid FROM pg_namespace WHERE nspname = tc.table_schema)
LEFT JOIN
    pg_description d ON d.objoid = c.oid AND d.objsubid = 0
WHERE
    tc.constraint_type = 'FOREIGN KEY'
    AND tc.table_schema NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
ORDER BY
    tc.table_schema, tc.table_name, kcu.ordinal_position;
 * Description:
 *   - Retrieves comprehensive foreign key relationships between tables
 *   - Includes constraint details, update/delete rules, and column mappings
 *   - Enhanced with business context and relationship metadata
 *   - Provides lineage information for data governance
 *
 * Parameters:
 *   {normalized_exclude_regex} - Regex pattern for schemas to exclude
 *   {normalized_include_regex} - Regex pattern for schemas to include
 *   {temp_table_regex_sql} - SQL fragment for additional table filtering
 */

SELECT
    tc.table_catalog AS database_name,
    tc.table_schema AS source_schema,
    tc.table_name AS source_table,
    kcu.column_name AS source_column,
    ccu.table_schema AS target_schema,
    ccu.table_name AS target_table,
    ccu.column_name AS target_column,
    tc.constraint_name,
    rc.update_rule,
    rc.delete_rule,
    tc.is_deferrable,
    tc.initially_deferred,
    pg_get_constraintdef(c.oid) AS constraint_definition,
    c.convalidated AS is_validated,
    c.connoinherit AS is_no_inherit,
    d.description AS constraint_description,
    kcu.ordinal_position AS column_position
FROM
    information_schema.table_constraints tc
JOIN
    information_schema.key_column_usage kcu
    ON tc.constraint_name = kcu.constraint_name
    AND tc.table_schema = kcu.table_schema
JOIN
    information_schema.constraint_column_usage ccu
    ON tc.constraint_name = ccu.constraint_name
    AND tc.table_schema = ccu.table_schema
JOIN
    information_schema.referential_constraints rc
    ON tc.constraint_name = rc.constraint_name
    AND tc.table_schema = rc.constraint_schema
JOIN
    pg_constraint c
    ON c.conname = tc.constraint_name
    AND c.connamespace = (SELECT oid FROM pg_namespace WHERE nspname = tc.table_schema)
LEFT JOIN
    pg_description d ON d.objoid = c.oid AND d.objsubid = 0
WHERE
    tc.constraint_type = 'FOREIGN KEY'
    AND tc.table_schema NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
    AND tc.table_schema !~ '{normalized_exclude_regex}'
    AND tc.table_schema ~ '{normalized_include_regex}'
    {temp_table_regex_sql}
ORDER BY
    tc.table_schema, tc.table_name, kcu.ordinal_position;