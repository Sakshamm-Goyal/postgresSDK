"""
PostgreSQL-specific handler for SourceSense metadata extraction.

This handler overrides the default SQL queries to use PostgreSQL syntax
instead of MySQL syntax, ensuring compatibility with PostgreSQL databases.
"""

from typing import Any, Dict

from application_sdk.handlers.sql import BaseSQLHandler


class PostgreSQLHandler(BaseSQLHandler):
    """
    PostgreSQL-specific handler that overrides SQL queries to use PostgreSQL syntax.
    
    This handler replaces MySQL-specific syntax like REGEXP with PostgreSQL equivalents
    like the ~ operator for regex matching.
    """
    
    # Override the tables check SQL to use PostgreSQL syntax
    tables_check_sql = """
    SELECT count(*) as count
    FROM information_schema.tables t
    WHERE t.table_schema NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
        AND CONCAT(t.table_catalog, '.', t.table_schema) !~ '{normalized_exclude_regex}'
        AND CONCAT(t.table_catalog, '.', t.table_schema) ~ '{normalized_include_regex}'
        {temp_table_regex_sql}
    """
    
    # Override the metadata SQL to use PostgreSQL syntax
    metadata_sql = """
    SELECT 
        s.schema_name, 
        s.catalog_name
    FROM information_schema.schemata s
    WHERE s.schema_name NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
        AND CONCAT(s.catalog_name, '.', s.schema_name) !~ '{normalized_exclude_regex}'
        AND CONCAT(s.catalog_name, '.', s.schema_name) ~ '{normalized_include_regex}'
    """
    
    # Override the client version SQL for PostgreSQL
    client_version_sql = """
    SELECT version() as version
    """
    
    # Override the test authentication SQL
    test_authentication_sql = """
    SELECT 1 as test
    """
    
    # Override the temp table regex SQL
    extract_temp_table_regex_table_sql = "AND t.table_name !~ '{exclude_table_regex}'"
    
    # Override the fetch databases SQL
    fetch_databases_sql = """
    SELECT 
        d.datname as database_name,
        pg_size_pretty(pg_database_size(d.datname)) as database_size,
        pg_encoding_to_char(d.encoding) as character_type,
        d.datcollate as collation,
        d.datconnlimit as connection_limit,
        CASE WHEN d.datallowconn THEN 'YES' ELSE 'NO' END as allows_connections,
        CASE WHEN d.datistemplate THEN 'YES' ELSE 'NO' END as is_template,
        pg_database_size(d.datname) as size_bytes,
        (SELECT count(*) FROM pg_stat_activity WHERE datname = d.datname) as active_connections
    FROM pg_database d
    WHERE d.datname NOT IN ('template0', 'template1', 'postgres')
        AND d.datname !~ '{normalized_exclude_regex}'
        AND d.datname ~ '{normalized_include_regex}'
    ORDER BY d.datname
    """
    
    # Override the fetch schemas SQL
    fetch_schemas_sql = """
    SELECT
        s.catalog_name,
        s.schema_name,
        s.schema_owner,
        s.default_character_set_catalog,
        s.default_character_set_schema,
        s.default_character_set_name,
        s.sql_path,
        obj_counts.table_count,
        obj_counts.view_count,
        obj_counts.materialized_view_count,
        obj_counts.foreign_table_count,
        obj_counts.total_objects,
        func_counts.function_count,
        func_counts.aggregate_count,
        func_counts.window_count,
        func_counts.procedure_count,
        d.description as description,
        CONCAT(s.catalog_name, '.', s.schema_name) as schema_qualified_name
    FROM information_schema.schemata s
    LEFT JOIN pg_catalog.pg_description d ON d.objoid = (SELECT oid FROM pg_namespace WHERE nspname = s.schema_name) AND d.objsubid = 0
    LEFT JOIN (
        SELECT
            table_schema,
            COUNT(CASE WHEN table_type = 'BASE TABLE' THEN 1 END) as table_count,
            COUNT(CASE WHEN table_type = 'VIEW' THEN 1 END) as view_count,
            COUNT(CASE WHEN table_type = 'FOREIGN TABLE' THEN 1 END) as foreign_table_count,
            COUNT(CASE WHEN table_type = 'MATERIALIZED VIEW' THEN 1 END) as materialized_view_count,
            COUNT(*) as total_objects
        FROM information_schema.tables
        WHERE table_catalog = '{database_name}'
        GROUP BY table_schema
    ) AS obj_counts ON s.schema_name = obj_counts.table_schema
    LEFT JOIN (
        SELECT
            n.nspname as schema_name,
            COUNT(CASE WHEN p.prokind = 'f' THEN 1 END) as function_count,
            COUNT(CASE WHEN p.prokind = 'a' THEN 1 END) as aggregate_count,
            COUNT(CASE WHEN p.prokind = 'w' THEN 1 END) as window_count,
            COUNT(CASE WHEN p.prokind = 'p' THEN 1 END) as procedure_count
        FROM pg_proc p
        JOIN pg_namespace n ON p.pronamespace = n.oid
        WHERE n.nspname = s.schema_name
        GROUP BY n.nspname
    ) AS func_counts ON s.schema_name = func_counts.schema_name
    WHERE s.catalog_name = '{database_name}'
        AND s.schema_name NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
        AND CONCAT(s.catalog_name, '.', s.schema_name) !~ '{normalized_exclude_regex}'
        AND CONCAT(s.catalog_name, '.', s.schema_name) ~ '{normalized_include_regex}'
    ORDER BY s.schema_name
    """