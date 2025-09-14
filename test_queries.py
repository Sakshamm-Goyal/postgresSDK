#!/usr/bin/env python3
"""
Test script to validate PostgreSQL queries and database connectivity.
This script helps debug issues with the SourceSense application.
"""

import asyncio
import os
import sys
from pathlib import Path
import psycopg2
from psycopg2.extras import RealDictCursor
import json

# Database connection parameters
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": "postgres",
    "password": "password",
    "database": "sample_db"
}

def get_db_connection():
    """Create a database connection."""
    try:
        conn = psycopg2.connect(**DB_CONFIG)
        return conn
    except Exception as e:
        print(f"Failed to connect to database: {e}")
        sys.exit(1)

def test_basic_connectivity():
    """Test basic database connectivity."""
    print("🔍 Testing basic database connectivity...")
    conn = get_db_connection()
    cursor = conn.cursor()
    
    cursor.execute("SELECT version();")
    version = cursor.fetchone()[0]
    print(f"✅ Connected to PostgreSQL: {version}")
    
    cursor.close()
    conn.close()

def test_schema_query():
    """Test the schema extraction query."""
    print("\n🔍 Testing schema extraction query...")
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    query = """
    SELECT
        s.schema_name,
        s.schema_owner,
        COALESCE(ss.table_count, 0) as table_count,
        COALESCE(ss.view_count, 0) as view_count,
        COALESCE(ss.total_objects, 0) as total_objects
    FROM information_schema.schemata s
    LEFT JOIN (
        SELECT 
            table_schema,
            COUNT(*) as total_objects,
            COUNT(CASE WHEN table_type = 'BASE TABLE' THEN 1 END) as table_count,
            COUNT(CASE WHEN table_type = 'VIEW' THEN 1 END) as view_count
        FROM information_schema.tables
        WHERE table_schema NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
        GROUP BY table_schema
    ) ss ON s.schema_name = ss.table_schema
    WHERE s.schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
    ORDER BY s.schema_name;
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    print(f"✅ Found {len(results)} schemas:")
    for row in results:
        print(f"  - {row['schema_name']}: {row['table_count']} tables, {row['view_count']} views")
    
    cursor.close()
    conn.close()
    return results

def test_table_query():
    """Test the table extraction query."""
    print("\n🔍 Testing table extraction query...")
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    query = """
    SELECT
        t.table_schema,
        t.table_name,
        t.table_type,
        COALESCE(s.n_live_tup, 0) AS estimated_row_count,
        pg_size_pretty(pg_total_relation_size(c.oid)) AS total_size
    FROM information_schema.tables t
    JOIN pg_class c ON c.relname = t.table_name AND c.relnamespace = (SELECT oid FROM pg_namespace WHERE nspname = t.table_schema)
    LEFT JOIN pg_stat_user_tables s ON s.relid = c.oid
    WHERE t.table_schema NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
    ORDER BY t.table_schema, t.table_name;
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    print(f"✅ Found {len(results)} tables:")
    for row in results:
        print(f"  - {row['table_schema']}.{row['table_name']}: {row['estimated_row_count']} rows, {row['total_size']}")
    
    cursor.close()
    conn.close()
    return results

def test_column_query():
    """Test the column extraction query."""
    print("\n🔍 Testing column extraction query...")
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    query = """
    SELECT
        c.table_schema,
        c.table_name,
        c.column_name,
        c.data_type,
        c.is_nullable,
        COALESCE(s.null_frac, 0) AS null_fraction,
        COALESCE(s.n_distinct, 0) AS distinct_values
    FROM information_schema.columns c
    LEFT JOIN pg_stats s ON s.schemaname = c.table_schema AND s.tablename = c.table_name AND s.attname = c.column_name
    WHERE c.table_schema NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
    ORDER BY c.table_schema, c.table_name, c.ordinal_position
    LIMIT 10;
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    print(f"✅ Found columns (showing first 10):")
    for row in results:
        print(f"  - {row['table_schema']}.{row['table_name']}.{row['column_name']}: {row['data_type']} (null: {row['null_fraction']:.2%})")
    
    cursor.close()
    conn.close()
    return results

def test_foreign_key_query():
    """Test the foreign key extraction query."""
    print("\n🔍 Testing foreign key extraction query...")
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    query = """
    SELECT
        tc.table_schema AS source_schema,
        tc.table_name AS source_table,
        kcu.column_name AS source_column,
        ccu.table_schema AS target_schema,
        ccu.table_name AS target_table,
        ccu.column_name AS target_column,
        tc.constraint_name
    FROM information_schema.table_constraints tc
    JOIN information_schema.key_column_usage kcu
        ON tc.constraint_name = kcu.constraint_name
        AND tc.table_schema = kcu.table_schema
    JOIN information_schema.constraint_column_usage ccu
        ON tc.constraint_name = ccu.constraint_name
        AND tc.table_schema = ccu.table_schema
    WHERE tc.constraint_type = 'FOREIGN KEY'
        AND tc.table_schema NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
    ORDER BY tc.table_schema, tc.table_name;
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    print(f"✅ Found {len(results)} foreign key relationships:")
    for row in results:
        print(f"  - {row['source_schema']}.{row['source_table']}.{row['source_column']} -> {row['target_schema']}.{row['target_table']}.{row['target_column']}")
    
    cursor.close()
    conn.close()
    return results

def test_data_quality_query():
    """Test the data quality extraction query."""
    print("\n🔍 Testing data quality extraction query...")
    conn = get_db_connection()
    cursor = conn.cursor(cursor_factory=RealDictCursor)
    
    query = """
    SELECT
        n.nspname AS schemaname,
        c.relname AS tablename,
        s.n_live_tup AS live_tuples,
        s.n_dead_tup AS dead_tuples,
        pg_size_pretty(pg_total_relation_size(c.oid)) AS total_size,
        CASE
            WHEN s.n_live_tup = 0 THEN 0
            ELSE GREATEST(0, 100 - (s.n_dead_tup * 100.0 / GREATEST(s.n_live_tup, 1)))
        END AS quality_score
    FROM pg_class c
    JOIN pg_namespace n ON c.relnamespace = n.oid
    LEFT JOIN pg_stat_user_tables s ON s.relid = c.oid
    WHERE c.relkind = 'r'
        AND n.nspname NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
    ORDER BY n.nspname, c.relname;
    """
    
    cursor.execute(query)
    results = cursor.fetchall()
    
    print(f"✅ Found {len(results)} tables with quality metrics:")
    for row in results:
        print(f"  - {row['schemaname']}.{row['tablename']}: {row['live_tuples']} rows, quality: {row['quality_score']:.1f}%, size: {row['total_size']}")
    
    cursor.close()
    conn.close()
    return results

def create_comprehensive_report():
    """Create a comprehensive report of the database."""
    print("\n📊 Creating comprehensive database report...")
    
    report = {
        "database_info": {
            "host": DB_CONFIG["host"],
            "port": DB_CONFIG["port"],
            "database": DB_CONFIG["database"]
        },
        "schemas": [],
        "tables": [],
        "foreign_keys": [],
        "data_quality": []
    }
    
    # Test all queries and collect results
    schemas = test_schema_query()
    tables = test_table_query()
    columns = test_column_query()
    foreign_keys = test_foreign_key_query()
    data_quality = test_data_quality_query()
    
    # Convert to JSON-serializable format
    report["schemas"] = [dict(row) for row in schemas]
    report["tables"] = [dict(row) for row in tables]
    report["foreign_keys"] = [dict(row) for row in foreign_keys]
    report["data_quality"] = [dict(row) for row in data_quality]
    
    # Save report
    report_file = Path("database_report.json")
    with open(report_file, "w") as f:
        json.dump(report, f, indent=2, default=str)
    
    print(f"\n📄 Comprehensive report saved to: {report_file}")
    print(f"📈 Summary:")
    print(f"  - Schemas: {len(schemas)}")
    print(f"  - Tables: {len(tables)}")
    print(f"  - Foreign Keys: {len(foreign_keys)}")
    print(f"  - Quality Metrics: {len(data_quality)}")

def main():
    """Main function to run all tests."""
    print("🚀 SourceSense PostgreSQL Database Test Suite")
    print("=" * 50)
    
    try:
        test_basic_connectivity()
        create_comprehensive_report()
        
        print("\n✅ All tests completed successfully!")
        print("🎉 SourceSense is ready to extract comprehensive PostgreSQL metadata!")
        
    except Exception as e:
        print(f"\n❌ Test failed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

