/*
 * File: extract_data_quality.sql
 * Purpose: Extracts data quality and profiling metrics
 *
 * Description:
 *   - Retrieves comprehensive data quality metrics at table level
 *   - Includes statistics on null values, cardinality, and data freshness
 *   - Enhanced with quality scoring and maintenance information
 *   - Provides profiling data for data governance
 *
 * Parameters:
 *   {normalized_exclude_regex} - Regex pattern for schemas to exclude
 *   {normalized_include_regex} - Regex pattern for schemas to include
 *   {temp_table_regex_sql} - SQL fragment for additional table filtering
 */

SELECT
    n.nspname AS schemaname,
    c.relname AS tablename,
    s.n_live_tup AS live_tuples,
    s.n_dead_tup AS dead_tuples,
    s.n_tup_ins AS total_inserts,
    s.n_tup_upd AS total_updates,
    s.n_tup_del AS total_deletes,
    s.last_vacuum,
    s.last_autovacuum,
    s.last_analyze,
    s.last_autoanalyze,
    s.vacuum_count,
    s.autovacuum_count,
    s.analyze_count,
    s.autoanalyze_count,
    EXTRACT(EPOCH FROM (NOW() - s.last_analyze)) / 3600 AS hours_since_last_analyze,
    EXTRACT(EPOCH FROM (NOW() - s.last_vacuum)) / 3600 AS hours_since_last_vacuum,
    CASE
        WHEN s.n_tup_ins + s.n_tup_upd + s.n_tup_del > 0
        THEN (s.n_tup_ins + s.n_tup_upd + s.n_tup_del - s.n_live_tup) * 100.0 / (s.n_tup_ins + s.n_tup_upd + s.n_tup_del)
        ELSE 0
    END AS change_ratio,
    CASE
        WHEN s.n_dead_tup > s.n_live_tup * 0.2 THEN 'HIGH'
        WHEN s.n_dead_tup > s.n_live_tup * 0.05 THEN 'MEDIUM'
        WHEN s.n_dead_tup > 0 THEN 'LOW'
        ELSE 'NONE'
    END AS dead_tuple_status,
    pg_total_relation_size(c.oid) AS total_size_bytes,
    pg_relation_size(c.oid) AS table_size_bytes,
    pg_indexes_size(c.oid) AS indexes_size_bytes,
    pg_size_pretty(pg_total_relation_size(c.oid)) AS total_size,
    pg_size_pretty(pg_relation_size(c.oid)) AS table_size,
    pg_size_pretty(pg_indexes_size(c.oid)) AS indexes_size,
    pg_size_pretty(pg_total_relation_size(c.reltoastrelid)) AS toast_size,
    -- Column profiling metrics
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_schema = n.nspname AND table_name = c.relname) AS total_columns,
    -- Quality score (simplified calculation)
    CASE
        WHEN s.n_live_tup = 0 THEN 0
        ELSE GREATEST(0, 100 - (s.n_dead_tup * 100.0 / GREATEST(s.n_live_tup, 1)))
    END AS quality_score,
    -- Freshness score (simplified calculation)
    CASE
        WHEN s.last_analyze IS NULL THEN 0
        ELSE GREATEST(0, 100 - (EXTRACT(EPOCH FROM (NOW() - s.last_analyze)) / 3600 / 24))
    END AS freshness_score,
    c.oid AS table_oid,
    n.oid AS schema_oid
FROM
    pg_class c
JOIN
    pg_namespace n ON c.relnamespace = n.oid
LEFT JOIN
    pg_stat_user_tables s ON s.relid = c.oid
WHERE
    c.relkind = 'r' -- Only regular tables
    AND n.nspname NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
ORDER BY
    n.nspname, c.relname;
 * Description:
 *   - Retrieves comprehensive data quality metrics at table level
 *   - Includes statistics on null values, cardinality, and data freshness
 *   - Enhanced with quality scoring and maintenance information
 *   - Provides profiling data for data governance
 *
 * Parameters:
 *   {normalized_exclude_regex} - Regex pattern for schemas to exclude
 *   {normalized_include_regex} - Regex pattern for schemas to include
 *   {temp_table_regex_sql} - SQL fragment for additional table filtering
 */

SELECT
    n.nspname AS schemaname,
    c.relname AS tablename,
    s.n_live_tup AS live_tuples,
    s.n_dead_tup AS dead_tuples,
    s.n_tup_ins AS total_inserts,
    s.n_tup_upd AS total_updates,
    s.n_tup_del AS total_deletes,
    s.last_vacuum,
    s.last_autovacuum,
    s.last_analyze,
    s.last_autoanalyze,
    s.vacuum_count,
    s.autovacuum_count,
    s.analyze_count,
    s.autoanalyze_count,
    EXTRACT(EPOCH FROM (NOW() - s.last_analyze)) / 3600 AS hours_since_last_analyze,
    EXTRACT(EPOCH FROM (NOW() - s.last_vacuum)) / 3600 AS hours_since_last_vacuum,
    CASE
        WHEN s.n_tup_ins + s.n_tup_upd + s.n_tup_del > 0
        THEN (s.n_tup_ins + s.n_tup_upd + s.n_tup_del - s.n_live_tup) * 100.0 / (s.n_tup_ins + s.n_tup_upd + s.n_tup_del)
        ELSE 0
    END AS change_ratio,
    CASE
        WHEN s.n_dead_tup > s.n_live_tup * 0.2 THEN 'HIGH'
        WHEN s.n_dead_tup > s.n_live_tup * 0.05 THEN 'MEDIUM'
        WHEN s.n_dead_tup > 0 THEN 'LOW'
        ELSE 'NONE'
    END AS dead_tuple_status,
    pg_total_relation_size(c.oid) AS total_size_bytes,
    pg_relation_size(c.oid) AS table_size_bytes,
    pg_indexes_size(c.oid) AS indexes_size_bytes,
    pg_size_pretty(pg_total_relation_size(c.oid)) AS total_size,
    pg_size_pretty(pg_relation_size(c.oid)) AS table_size,
    pg_size_pretty(pg_indexes_size(c.oid)) AS indexes_size,
    pg_size_pretty(pg_total_relation_size(c.reltoastrelid)) AS toast_size,
    -- Column profiling metrics
    (SELECT COUNT(*) FROM information_schema.columns WHERE table_schema = n.nspname AND table_name = c.relname) AS total_columns,
    -- Quality score (simplified calculation)
    CASE
        WHEN s.n_live_tup = 0 THEN 0
        ELSE GREATEST(0, 100 - (s.n_dead_tup * 100.0 / GREATEST(s.n_live_tup, 1)))
    END AS quality_score,
    -- Freshness score (simplified calculation)
    CASE
        WHEN s.last_analyze IS NULL THEN 0
        ELSE GREATEST(0, 100 - (EXTRACT(EPOCH FROM (NOW() - s.last_analyze)) / 3600 / 24))
    END AS freshness_score,
    c.oid AS table_oid,
    n.oid AS schema_oid
FROM
    pg_class c
JOIN
    pg_namespace n ON c.relnamespace = n.oid
LEFT JOIN
    pg_stat_user_tables s ON s.relid = c.oid
WHERE
    c.relkind = 'r' -- Only regular tables
    AND n.nspname NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
    AND n.nspname !~ '{normalized_exclude_regex}'
    AND n.nspname ~ '{normalized_include_regex}'
    {temp_table_regex_sql}
ORDER BY
    n.nspname, c.relname;