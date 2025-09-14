/*
 * File: extract_table.sql
 * Purpose: Extracts table metadata from PostgreSQL server
 *
 * Description:
 *   - Retrieves comprehensive table information including statistics and constraints
 *   - Determines table type, partitioning, and storage information
 *   - Includes row estimates, size information, and data quality metrics
 *   - Enhanced with business context and lineage information
 *
 * Parameters:
 *   {normalized_exclude_regex} - Regex pattern for schemas to exclude
 *   {normalized_include_regex} - Regex pattern for schemas to include
 *   {temp_table_regex_sql} - SQL fragment for additional table filtering
 */

SELECT
    t.table_catalog,
    t.table_schema,
    t.table_name,
    CASE
        WHEN t.table_type = 'BASE TABLE' THEN 'TABLE'
        WHEN t.table_type = 'VIEW' THEN 'VIEW'
        WHEN t.table_type = 'FOREIGN TABLE' THEN 'FOREIGN_TABLE'
        WHEN t.table_type = 'MATERIALIZED VIEW' THEN 'MATERIALIZED_VIEW'
        ELSE t.table_type
    END AS table_type,
    COALESCE(s.n_live_tup, 0) AS estimated_row_count,
    COALESCE(s.n_dead_tup, 0) AS dead_row_count,
    COALESCE(s.n_tup_ins, 0) AS total_inserts,
    COALESCE(s.n_tup_upd, 0) AS total_updates,
    COALESCE(s.n_tup_del, 0) AS total_deletes,
    s.last_vacuum,
    s.last_analyze,
    s.vacuum_count,
    s.analyze_count,
    pg_size_pretty(pg_total_relation_size(c.oid)) AS total_size,
    pg_total_relation_size(c.oid) AS total_size_bytes,
    pg_size_pretty(pg_relation_size(c.oid)) AS table_size,
    pg_relation_size(c.oid) AS table_size_bytes,
    pg_size_pretty(pg_indexes_size(c.oid)) AS indexes_size,
    pg_indexes_size(c.oid) AS indexes_size_bytes,
    (SELECT count(*) FROM pg_constraint WHERE conrelid = c.oid) AS constraint_count,
    (SELECT count(*) FROM pg_constraint WHERE conrelid = c.oid AND contype = 'p') AS primary_key_count,
    (SELECT count(*) FROM pg_constraint WHERE conrelid = c.oid AND contype = 'f') AS foreign_key_count,
    (SELECT count(*) FROM pg_constraint WHERE conrelid = c.oid AND contype = 'u') AS unique_constraint_count,
    (SELECT count(*) FROM pg_constraint WHERE conrelid = c.oid AND contype = 'c') AS check_constraint_count,
    (SELECT count(*) FROM pg_index WHERE indrelid = c.oid) AS index_count,
    (SELECT count(*) FROM pg_index WHERE indrelid = c.oid AND indisunique) AS unique_index_count,
    (SELECT count(*) FROM pg_index WHERE indrelid = c.oid AND indisprimary) AS primary_index_count,
    d.description AS description,
    CASE WHEN p.partrelid IS NOT NULL THEN TRUE ELSE FALSE END AS is_partitioned,
    pg_get_partkeydef(c.oid) AS partition_strategy,
    (SELECT count(*) FROM pg_partitioned_table WHERE partrelid = c.oid) AS partition_column_count,
    c.oid AS table_oid,
    n.oid AS schema_oid
FROM
    information_schema.tables t
JOIN
    pg_class c ON c.relname = t.table_name AND c.relnamespace = (SELECT oid FROM pg_namespace WHERE nspname = t.table_schema)
JOIN
    pg_namespace n ON n.oid = c.relnamespace
LEFT JOIN
    pg_stat_user_tables s ON s.relid = c.oid
LEFT JOIN
    pg_description d ON d.objoid = c.oid AND d.objsubid = 0
LEFT JOIN
    pg_partitioned_table p ON p.partrelid = c.oid
WHERE
    t.table_schema NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
    AND t.table_schema !~ '{normalized_exclude_regex}'
    AND t.table_schema ~ '{normalized_include_regex}'
    {temp_table_regex_sql}
ORDER BY
    t.table_schema, t.table_name;