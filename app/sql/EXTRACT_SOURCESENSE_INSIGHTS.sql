/*
 * File: EXTRACT_SOURCESENSE_INSIGHTS.sql
 * Purpose: Extracts SourceSense unique insights and recommendations
 *
 * Description:
 *   - Provides unique insights about database health, optimization opportunities
 *   - Generates recommendations for data governance and quality improvements
 *   - Calculates advanced metrics not available in standard metadata
 *   - Creates actionable insights for data teams
 */

-- Schema-level insights
SELECT 
    'SCHEMA_INSIGHT' AS insight_type,
    n.nspname AS entity_name,
    NULL AS table_name,
    json_build_object(
        'table_count', COUNT(DISTINCT c.relname),
        'total_size_mb', ROUND(COALESCE(SUM(pg_total_relation_size(c.oid)) / 1024.0 / 1024.0, 0)::numeric, 2),
        'avg_table_size', ROUND(COALESCE(AVG(pg_total_relation_size(c.oid)) / 1024.0 / 1024.0, 0)::numeric, 2),
        'foreign_key_count', (SELECT COUNT(*) FROM information_schema.referential_constraints rc WHERE rc.constraint_schema = n.nspname),
        'index_count', (SELECT COUNT(*) FROM pg_indexes pi WHERE pi.schemaname = n.nspname)
    ) AS insights,
    CASE 
        WHEN COUNT(DISTINCT c.relname) > 5 THEN 'Large schema - consider partitioning strategy'
        WHEN COUNT(DISTINCT c.relname) = 0 THEN 'Empty schema - consider cleanup'
        ELSE 'Schema appears well-sized'
    END AS recommendation,
    NOW() AS generated_at
FROM pg_namespace n
LEFT JOIN pg_class c ON c.relnamespace = n.oid AND c.relkind = 'r'
WHERE n.nspname NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
GROUP BY n.nspname

UNION ALL

-- Table-level insights
SELECT 
    'TABLE_INSIGHT' AS insight_type,
    n.nspname AS entity_name,
    c.relname AS table_name,
    json_build_object(
        'row_count', COALESCE(s.n_live_tup, 0),
        'size_mb', ROUND((pg_total_relation_size(c.oid) / 1024.0 / 1024.0)::numeric, 2),
        'bloat_percentage', CASE 
            WHEN s.n_live_tup = 0 THEN 0
            ELSE ROUND((s.n_dead_tup::float / s.n_live_tup::float * 100)::numeric, 2)
        END,
        'stats_freshness', CASE 
            WHEN s.last_analyze IS NULL THEN 'NEVER'
            WHEN s.last_analyze < NOW() - INTERVAL '30 days' THEN 'CRITICAL'
            WHEN s.last_analyze < NOW() - INTERVAL '7 days' THEN 'WARNING'
            ELSE 'GOOD'
        END,
        'quality_score', CASE 
            WHEN s.n_live_tup = 0 THEN 0
            ELSE GREATEST(0, 100 - (s.n_dead_tup::float / s.n_live_tup::float * 50) - 
                         (CASE WHEN s.last_analyze < NOW() - INTERVAL '7 days' THEN 25 ELSE 0 END))
        END
    ) AS insights,
    CASE 
        WHEN s.last_analyze IS NULL OR s.last_analyze < NOW() - INTERVAL '30 days' THEN 'URGENT: Run ANALYZE on this table'
        WHEN s.n_dead_tup > s.n_live_tup * 0.1 THEN 'Consider VACUUM to reduce bloat'
        WHEN s.n_live_tup = 0 THEN 'Empty table - consider cleanup'
        ELSE 'Table appears healthy'
    END AS recommendation,
    NOW() AS generated_at
FROM pg_namespace n
JOIN pg_class c ON c.relnamespace = n.oid AND c.relkind = 'r'
LEFT JOIN pg_stat_user_tables s ON s.relid = c.oid
WHERE n.nspname NOT IN ('pg_catalog', 'information_schema', 'pg_toast')

UNION ALL

-- Column-level insights
SELECT 
    'COLUMN_INSIGHT' AS insight_type,
    schemaname AS entity_name,
    tablename AS table_name,
    json_build_object(
        'total_columns', COUNT(*),
        'high_null_columns', COUNT(CASE WHEN null_frac > 0.5 THEN 1 END),
        'constant_columns', COUNT(CASE WHEN n_distinct = 1 THEN 1 END),
        'low_cardinality_columns', COUNT(CASE WHEN n_distinct < 0 AND ABS(n_distinct) < 0.01 THEN 1 END),
        'avg_null_percentage', ROUND((AVG(null_frac) * 100)::numeric, 2)
    ) AS insights,
    CASE 
        WHEN COUNT(CASE WHEN null_frac > 0.5 THEN 1 END) > COUNT(*) * 0.3 THEN 'High null rate detected - review data collection'
        WHEN COUNT(CASE WHEN n_distinct = 1 THEN 1 END) > 0 THEN 'Remove or review constant columns'
        WHEN COUNT(CASE WHEN n_distinct < 0 AND ABS(n_distinct) < 0.01 THEN 1 END) > COUNT(*) * 0.5 THEN 'Consider indexing strategy for low-cardinality columns'
        ELSE 'Column distribution appears normal'
    END AS recommendation,
    NOW() AS generated_at
FROM pg_stats
WHERE schemaname NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
GROUP BY schemaname, tablename

ORDER BY insight_type, entity_name, table_name;

