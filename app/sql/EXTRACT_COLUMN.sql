/*
 * File: extract_column.sql
 * Purpose: Extracts column metadata from PostgreSQL server
 *
 * Description:
 *   - Retrieves comprehensive column information including data types, constraints, and statistics
 *   - Includes data quality metrics (null counts, distinct values, etc.)
 *   - Enhanced with business context, descriptions, and lineage information
 *   - Provides detailed constraint and index information
 *
 * Parameters:
 *   {normalized_exclude_regex} - Regex pattern for schemas to exclude
 *   {normalized_include_regex} - Regex pattern for schemas to include
 *   {temp_table_regex_sql} - SQL fragment for additional table filtering
 */

SELECT
    c.table_catalog,
    c.table_schema,
    c.table_name,
    c.column_name,
    c.ordinal_position,
    c.is_nullable,
    c.data_type,
    c.column_default,
    c.character_maximum_length,
    c.character_octet_length,
    c.numeric_precision,
    c.numeric_precision_radix,
    c.numeric_scale,
    c.datetime_precision,
    c.interval_type,
    c.interval_precision,
    c.character_set_catalog,
    c.character_set_schema,
    c.character_set_name,
    c.collation_catalog,
    c.collation_schema,
    c.collation_name,
    c.domain_catalog,
    c.domain_schema,
    c.domain_name,
    c.udt_catalog,
    c.udt_schema,
    c.udt_name,
    c.is_identity,
    c.identity_generation,
    c.identity_start,
    c.identity_increment,
    c.identity_maximum,
    c.identity_minimum,
    c.identity_cycle,
    c.is_generated,
    c.generation_expression,
    c.is_updatable,
    pg_description.description,
    -- Data quality metrics from pg_stats
    COALESCE(s.n_distinct, 0) AS distinct_value_count,
    COALESCE(s.null_frac, 0) AS null_fraction,
    COALESCE(s.avg_width, 0) AS average_width,
    COALESCE(s.correlation, 0) AS correlation,
    s.most_common_vals AS most_common_values,
    s.most_common_freqs AS most_common_frequencies,
    s.histogram_bounds AS histogram_bounds,
    -- Constraint information
    (SELECT conname FROM pg_constraint WHERE conrelid = t.oid AND conkey @> ARRAY[a.attnum] AND contype = 'p' LIMIT 1) AS primary_key_name,
    (SELECT conname FROM pg_constraint WHERE conrelid = t.oid AND conkey @> ARRAY[a.attnum] AND contype = 'f' LIMIT 1) AS foreign_key_name,
    (SELECT conname FROM pg_constraint WHERE conrelid = t.oid AND conkey @> ARRAY[a.attnum] AND contype = 'u' LIMIT 1) AS unique_constraint_name,
    -- Index information
    (SELECT count(*) FROM pg_index ix WHERE ix.indrelid = t.oid AND a.attnum = ANY(ix.indkey)) AS index_count,
    (SELECT count(*) FROM pg_index ix WHERE ix.indrelid = t.oid AND a.attnum = ANY(ix.indkey) AND ix.indisunique) AS unique_index_count,
    (SELECT count(*) FROM pg_index ix WHERE ix.indrelid = t.oid AND a.attnum = ANY(ix.indkey) AND ix.indisprimary) AS primary_index_count,
    -- Sequence information (if column is linked to a sequence)
    (SELECT s.relname FROM pg_class s JOIN pg_depend d ON s.oid = d.objid WHERE d.refobjid = t.oid AND d.refobjsubid = a.attnum AND s.relkind = 'S') AS sequence_name,
    format_type(a.atttypid, a.atttypmod) AS full_data_type,
    CASE WHEN c.is_identity = 'YES' THEN c.identity_generation ELSE 'NONE' END AS auto_increment_type,
    a.attnum AS column_position,
    t.oid AS table_oid,
    a.attrelid AS attribute_relation_id
FROM
    information_schema.columns c
JOIN
    pg_class t ON t.relname = c.table_name AND t.relnamespace = (SELECT oid FROM pg_namespace WHERE nspname = c.table_schema)
JOIN
    pg_attribute a ON a.attrelid = t.oid AND a.attname = c.column_name
LEFT JOIN
    pg_stats s ON s.schemaname = c.table_schema AND s.tablename = c.table_name AND s.attname = c.column_name
LEFT JOIN
    pg_description ON pg_description.objoid = a.attrelid AND pg_description.objsubid = a.attnum
WHERE
    c.table_schema NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
    AND c.table_schema !~ '{normalized_exclude_regex}'
    AND c.table_schema ~ '{normalized_include_regex}'
    {temp_table_regex_sql}
ORDER BY
    c.table_schema, c.table_name, c.ordinal_position;