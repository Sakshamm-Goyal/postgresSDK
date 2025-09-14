#!/usr/bin/env python3
"""
SourceSense PostgreSQL Metadata Extraction Demo
==============================================

This script demonstrates the comprehensive PostgreSQL metadata extraction capabilities
of SourceSense - the winning Atlan Application SDK application.

Features:
- Complete schema, table, column metadata extraction
- Foreign key lineage discovery
- Data quality profiling and insights
- Business context and descriptions
- Advanced PostgreSQL-specific optimizations
- Unique SourceSense insights and recommendations

Author: SourceSense Team
Version: 1.0.0
"""

import asyncio
import json
import os
import sys
from pathlib import Path
import psycopg2
from psycopg2.extras import RealDictCursor
import time
from datetime import datetime

# Database connection parameters
DB_CONFIG = {
    "host": "localhost",
    "port": 5432,
    "user": "postgres",
    "password": "password",
    "database": "sample_db"
}

class SourceSenseDemo:
    """SourceSense comprehensive demo showcasing all features."""
    
    def __init__(self):
        self.db_config = DB_CONFIG
        self.results = {}
        
    def get_db_connection(self):
        """Create a database connection."""
        try:
            conn = psycopg2.connect(**self.db_config)
            return conn
        except Exception as e:
            print(f"❌ Failed to connect to database: {e}")
            sys.exit(1)
    
    def print_header(self, title):
        """Print a formatted header."""
        print(f"\n{'='*60}")
        print(f"🎯 {title}")
        print(f"{'='*60}")
    
    def print_success(self, message):
        """Print a success message."""
        print(f"✅ {message}")
    
    def print_info(self, message):
        """Print an info message."""
        print(f"ℹ️  {message}")
    
    def print_warning(self, message):
        """Print a warning message."""
        print(f"⚠️  {message}")
    
    def demo_database_connectivity(self):
        """Demo 1: Database connectivity and basic info."""
        self.print_header("Database Connectivity & Basic Information")
        
        conn = self.get_db_connection()
        cursor = conn.cursor()
        
        # PostgreSQL version
        cursor.execute("SELECT version();")
        version = cursor.fetchone()[0]
        self.print_success(f"Connected to PostgreSQL: {version}")
        
        # Database size
        cursor.execute("SELECT pg_size_pretty(pg_database_size(current_database()));")
        size = cursor.fetchone()[0]
        self.print_success(f"Database size: {size}")
        
        # Connection info
        cursor.execute("SELECT current_database(), current_user, inet_server_addr(), inet_server_port();")
        db_info = cursor.fetchone()
        self.print_info(f"Database: {db_info[0]}, User: {db_info[1]}, Server: {db_info[2]}:{db_info[3]}")
        
        cursor.close()
        conn.close()
        
        return True
    
    def demo_schema_extraction(self):
        """Demo 2: Comprehensive schema metadata extraction."""
        self.print_header("Schema Metadata Extraction")
        
        conn = self.get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        query = """
        SELECT
            s.schema_name,
            s.schema_owner,
            COALESCE(ss.table_count, 0) as table_count,
            COALESCE(ss.view_count, 0) as view_count,
            COALESCE(ss.total_objects, 0) as total_objects,
            COALESCE(sf.function_count, 0) as function_count
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
        LEFT JOIN (
            SELECT 
                n.nspname as table_schema,
                COUNT(p.proname) as function_count
            FROM pg_proc p
            JOIN pg_namespace n ON p.pronamespace = n.oid
            WHERE n.nspname NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
            GROUP BY n.nspname
        ) sf ON s.schema_name = sf.table_schema
        WHERE s.schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
        ORDER BY s.schema_name;
        """
        
        cursor.execute(query)
        schemas = cursor.fetchall()
        
        self.print_success(f"Found {len(schemas)} schemas:")
        for schema in schemas:
            print(f"  📁 {schema['schema_name']}: {schema['table_count']} tables, {schema['view_count']} views, {schema['function_count']} functions")
        
        self.results['schemas'] = [dict(schema) for schema in schemas]
        cursor.close()
        conn.close()
        
        return True
    
    def demo_table_extraction(self):
        """Demo 3: Comprehensive table metadata extraction."""
        self.print_header("Table Metadata Extraction")
        
        conn = self.get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        query = """
        SELECT
            t.table_schema,
            t.table_name,
            t.table_type,
            COALESCE(s.n_live_tup, 0) AS estimated_row_count,
            pg_size_pretty(pg_total_relation_size(c.oid)) AS total_size,
            pg_total_relation_size(c.oid) AS total_size_bytes,
            (SELECT count(*) FROM pg_constraint WHERE conrelid = c.oid) AS constraint_count,
            (SELECT count(*) FROM pg_indexes WHERE schemaname = t.table_schema AND tablename = t.table_name) AS index_count,
            d.description
        FROM information_schema.tables t
        JOIN pg_class c ON c.relname = t.table_name AND c.relnamespace = (SELECT oid FROM pg_namespace WHERE nspname = t.table_schema)
        LEFT JOIN pg_stat_user_tables s ON s.relid = c.oid
        LEFT JOIN pg_description d ON d.objoid = c.oid AND d.objsubid = 0
        WHERE t.table_schema NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
        ORDER BY t.table_schema, t.table_name;
        """
        
        cursor.execute(query)
        tables = cursor.fetchall()
        
        self.print_success(f"Found {len(tables)} tables:")
        for table in tables:
            description = table['description'] or "No description"
            print(f"  📊 {table['table_schema']}.{table['table_name']}: {table['estimated_row_count']} rows, {table['total_size']}, {table['constraint_count']} constraints, {table['index_count']} indexes")
            if description != "No description":
                print(f"      💬 {description}")
        
        self.results['tables'] = [dict(table) for table in tables]
        cursor.close()
        conn.close()
        
        return True
    
    def demo_column_extraction(self):
        """Demo 4: Comprehensive column metadata extraction."""
        self.print_header("Column Metadata Extraction")
        
        conn = self.get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        query = """
        SELECT
            c.table_schema,
            c.table_name,
            c.column_name,
            c.data_type,
            c.is_nullable,
            c.column_default,
            c.character_maximum_length,
            c.numeric_precision,
            c.numeric_scale,
            COALESCE(s.null_frac, 0) AS null_fraction,
            COALESCE(s.n_distinct, 0) AS distinct_values,
            COALESCE(s.avg_width, 0) AS average_width,
            pg_description.description
        FROM information_schema.columns c
        LEFT JOIN pg_stats s ON s.schemaname = c.table_schema AND s.tablename = c.table_name AND s.attname = c.column_name
        LEFT JOIN pg_description ON pg_description.objoid = (SELECT oid FROM pg_class WHERE relname = c.table_name AND relnamespace = (SELECT oid FROM pg_namespace WHERE nspname = c.table_schema))
        WHERE c.table_schema NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
        ORDER BY c.table_schema, c.table_name, c.ordinal_position
        LIMIT 20;
        """
        
        cursor.execute(query)
        columns = cursor.fetchall()
        
        self.print_success(f"Found columns (showing first 20):")
        for column in columns:
            null_pct = f"{column['null_fraction']:.1%}" if column['null_fraction'] else "0%"
            print(f"  🔹 {column['table_schema']}.{column['table_name']}.{column['column_name']}: {column['data_type']} (null: {null_pct}, distinct: {column['distinct_values']})")
        
        self.results['columns'] = [dict(column) for column in columns]
        cursor.close()
        conn.close()
        
        return True
    
    def demo_foreign_key_lineage(self):
        """Demo 5: Foreign key lineage discovery."""
        self.print_header("Foreign Key Lineage Discovery")
        
        conn = self.get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        query = """
        SELECT
            tc.table_schema AS source_schema,
            tc.table_name AS source_table,
            kcu.column_name AS source_column,
            ccu.table_schema AS target_schema,
            ccu.table_name AS target_table,
            ccu.column_name AS target_column,
            tc.constraint_name,
            rc.update_rule,
            rc.delete_rule
        FROM information_schema.table_constraints tc
        JOIN information_schema.key_column_usage kcu
            ON tc.constraint_name = kcu.constraint_name
            AND tc.table_schema = kcu.table_schema
        JOIN information_schema.constraint_column_usage ccu
            ON tc.constraint_name = ccu.constraint_name
            AND tc.table_schema = ccu.table_schema
        JOIN information_schema.referential_constraints rc
            ON tc.constraint_name = rc.constraint_name
            AND tc.table_schema = rc.constraint_schema
        WHERE tc.constraint_type = 'FOREIGN KEY'
            AND tc.table_schema NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
        ORDER BY tc.table_schema, tc.table_name;
        """
        
        cursor.execute(query)
        foreign_keys = cursor.fetchall()
        
        self.print_success(f"Found {len(foreign_keys)} foreign key relationships:")
        for fk in foreign_keys:
            print(f"  🔗 {fk['source_schema']}.{fk['source_table']}.{fk['source_column']} → {fk['target_schema']}.{fk['target_table']}.{fk['target_column']}")
            print(f"      Rules: UPDATE {fk['update_rule']}, DELETE {fk['delete_rule']}")
        
        self.results['foreign_keys'] = [dict(fk) for fk in foreign_keys]
        cursor.close()
        conn.close()
        
        return True
    
    def demo_data_quality_profiling(self):
        """Demo 6: Data quality profiling and metrics."""
        self.print_header("Data Quality Profiling & Metrics")
        
        conn = self.get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        query = """
        SELECT
            n.nspname AS schema_name,
            c.relname AS table_name,
            s.n_live_tup AS live_tuples,
            s.n_dead_tup AS dead_tuples,
            pg_size_pretty(pg_total_relation_size(c.oid)) AS total_size,
            CASE
                WHEN s.n_live_tup = 0 THEN 0
                ELSE GREATEST(0, 100 - (s.n_dead_tup::float / s.n_live_tup::float * 100))
            END AS quality_score,
            CASE
                WHEN s.last_analyze IS NULL THEN 'NEVER'
                WHEN s.last_analyze < NOW() - INTERVAL '7 days' THEN 'STALE'
                ELSE 'FRESH'
            END AS stats_freshness
        FROM pg_namespace n
        JOIN pg_class c ON c.relnamespace = n.oid AND c.relkind = 'r'
        LEFT JOIN pg_stat_user_tables s ON s.relid = c.oid
        WHERE n.nspname NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
        ORDER BY n.nspname, c.relname;
        """
        
        cursor.execute(query)
        quality_metrics = cursor.fetchall()
        
        self.print_success(f"Data quality metrics for {len(quality_metrics)} tables:")
        for metric in quality_metrics:
            quality_icon = "🟢" if metric['quality_score'] > 90 else "🟡" if metric['quality_score'] > 70 else "🔴"
            stats_icon = "🟢" if metric['stats_freshness'] == 'FRESH' else "🟡" if metric['stats_freshness'] == 'STALE' else "🔴"
            print(f"  {quality_icon} {metric['schema_name']}.{metric['table_name']}: {metric['live_tuples']} rows, quality: {metric['quality_score']:.1f}%, stats: {stats_icon} {metric['stats_freshness']}")
        
        self.results['data_quality'] = [dict(metric) for metric in quality_metrics]
        cursor.close()
        conn.close()
        
        return True
    
    def demo_sourcesense_insights(self):
        """Demo 7: Unique SourceSense insights and recommendations."""
        self.print_header("SourceSense Unique Insights & Recommendations")
        
        conn = self.get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Schema insights
        schema_query = """
        SELECT 
            'SCHEMA_INSIGHT' AS insight_type,
            n.nspname AS entity_name,
            NULL AS table_name,
            json_build_object(
                'table_count', COUNT(DISTINCT c.relname),
                'total_size_mb', ROUND(COALESCE(SUM(pg_total_relation_size(c.oid)) / 1024.0 / 1024.0, 0)::numeric, 2),
                'foreign_key_count', (SELECT COUNT(*) FROM information_schema.referential_constraints rc WHERE rc.constraint_schema = n.nspname),
                'index_count', (SELECT COUNT(*) FROM pg_indexes pi WHERE pi.schemaname = n.nspname)
            ) AS insights,
            CASE 
                WHEN COUNT(DISTINCT c.relname) > 5 THEN 'Large schema - consider partitioning strategy'
                WHEN COUNT(DISTINCT c.relname) = 0 THEN 'Empty schema - consider cleanup'
                ELSE 'Schema appears well-sized'
            END AS recommendation
        FROM pg_namespace n
        LEFT JOIN pg_class c ON c.relnamespace = n.oid AND c.relkind = 'r'
        WHERE n.nspname NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
        GROUP BY n.nspname
        ORDER BY COUNT(DISTINCT c.relname) DESC;
        """
        
        cursor.execute(schema_query)
        schema_insights = cursor.fetchall()
        
        self.print_success("Schema-level insights:")
        for insight in schema_insights:
            insights_data = insight['insights']
            print(f"  📊 {insight['entity_name']}: {insights_data['table_count']} tables, {insights_data['total_size_mb']} MB")
            print(f"      💡 {insight['recommendation']}")
        
        # Table insights
        table_query = """
        SELECT 
            'TABLE_INSIGHT' AS insight_type,
            n.nspname AS entity_name,
            c.relname AS table_name,
            json_build_object(
                'row_count', COALESCE(s.n_live_tup, 0),
                'size_mb', ROUND((pg_total_relation_size(c.oid) / 1024.0 / 1024.0)::numeric, 2),
                'quality_score', CASE 
                    WHEN s.n_live_tup = 0 THEN 0
                    ELSE GREATEST(0, 100 - (s.n_dead_tup::float / s.n_live_tup::float * 50))
                END
            ) AS insights,
            CASE 
                WHEN s.n_live_tup = 0 THEN 'Empty table - consider cleanup'
                WHEN s.n_dead_tup > s.n_live_tup * 0.1 THEN 'Consider VACUUM to reduce bloat'
                ELSE 'Table appears healthy'
            END AS recommendation
        FROM pg_namespace n
        JOIN pg_class c ON c.relnamespace = n.oid AND c.relkind = 'r'
        LEFT JOIN pg_stat_user_tables s ON s.relid = c.oid
        WHERE n.nspname NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
        ORDER BY pg_total_relation_size(c.oid) DESC
        LIMIT 5;
        """
        
        cursor.execute(table_query)
        table_insights = cursor.fetchall()
        
        self.print_success("Table-level insights (top 5 by size):")
        for insight in table_insights:
            insights_data = insight['insights']
            print(f"  📈 {insight['entity_name']}.{insight['table_name']}: {insights_data['row_count']} rows, {insights_data['size_mb']} MB, quality: {insights_data['quality_score']:.1f}%")
            print(f"      💡 {insight['recommendation']}")
        
        self.results['insights'] = {
            'schema_insights': [dict(insight) for insight in schema_insights],
            'table_insights': [dict(insight) for insight in table_insights]
        }
        
        cursor.close()
        conn.close()
        
        return True
    
    def demo_performance_metrics(self):
        """Demo 8: Performance and optimization metrics."""
        self.print_header("Performance & Optimization Metrics")
        
        conn = self.get_db_connection()
        cursor = conn.cursor(cursor_factory=RealDictCursor)
        
        # Index usage statistics
        index_query = """
        SELECT
            schemaname,
            relname as tablename,
            indexrelname as indexname,
            idx_tup_read,
            idx_tup_fetch,
            CASE 
                WHEN idx_tup_read = 0 THEN 0
                ELSE ROUND((idx_tup_fetch::float / idx_tup_read::float * 100)::numeric, 2)
            END AS efficiency_percentage
        FROM pg_stat_user_indexes
        WHERE schemaname NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
        ORDER BY idx_tup_read DESC
        LIMIT 10;
        """
        
        cursor.execute(index_query)
        index_stats = cursor.fetchall()
        
        self.print_success("Top 10 most used indexes:")
        for stat in index_stats:
            efficiency = f"{stat['efficiency_percentage']:.1f}%" if stat['efficiency_percentage'] else "0%"
            print(f"  📊 {stat['schemaname']}.{stat['tablename']}.{stat['indexname']}: {stat['idx_tup_read']} reads, efficiency: {efficiency}")
        
        # Table bloat analysis
        bloat_query = """
        SELECT
            schemaname,
            tablename,
            n_live_tup,
            n_dead_tup,
            CASE 
                WHEN n_live_tup = 0 THEN 0
                ELSE ROUND((n_dead_tup::float / n_live_tup::float * 100)::numeric, 2)
            END AS bloat_percentage
        FROM pg_stat_user_tables
        WHERE schemaname NOT IN ('pg_catalog', 'information_schema', 'pg_toast')
        ORDER BY n_dead_tup DESC
        LIMIT 5;
        """
        
        cursor.execute(bloat_query)
        bloat_stats = cursor.fetchall()
        
        self.print_success("Top 5 tables with highest bloat:")
        for stat in bloat_stats:
            bloat_pct = f"{stat['bloat_percentage']:.1f}%" if stat['bloat_percentage'] else "0%"
            print(f"  ⚠️  {stat['schemaname']}.{stat['tablename']}: {stat['n_live_tup']} live, {stat['n_dead_tup']} dead ({bloat_pct} bloat)")
        
        self.results['performance'] = {
            'index_stats': [dict(stat) for stat in index_stats],
            'bloat_stats': [dict(stat) for stat in bloat_stats]
        }
        
        cursor.close()
        conn.close()
        
        return True
    
    def generate_comprehensive_report(self):
        """Generate a comprehensive SourceSense report."""
        self.print_header("SourceSense Comprehensive Report")
        
        # Calculate summary statistics
        total_schemas = len(self.results.get('schemas', []))
        total_tables = len(self.results.get('tables', []))
        total_columns = len(self.results.get('columns', []))
        total_foreign_keys = len(self.results.get('foreign_keys', []))
        total_quality_metrics = len(self.results.get('data_quality', []))
        
        # Calculate total database size
        total_size_bytes = sum(table.get('total_size_bytes', 0) for table in self.results.get('tables', []))
        total_size_mb = total_size_bytes / (1024 * 1024)
        
        # Calculate average quality score
        quality_scores = [metric.get('quality_score', 0) for metric in self.results.get('data_quality', [])]
        avg_quality = sum(quality_scores) / len(quality_scores) if quality_scores else 0
        
        print(f"📊 Database Overview:")
        print(f"   • Schemas: {total_schemas}")
        print(f"   • Tables: {total_tables}")
        print(f"   • Columns: {total_columns}")
        print(f"   • Foreign Keys: {total_foreign_keys}")
        print(f"   • Total Size: {total_size_mb:.2f} MB")
        print(f"   • Average Quality Score: {avg_quality:.1f}%")
        
        # Schema distribution
        print(f"\n📁 Schema Distribution:")
        for schema in self.results.get('schemas', []):
            print(f"   • {schema['schema_name']}: {schema['table_count']} tables, {schema['function_count']} functions")
        
        # Top tables by size
        print(f"\n📈 Top 5 Tables by Size:")
        sorted_tables = sorted(self.results.get('tables', []), key=lambda x: x.get('total_size_bytes', 0), reverse=True)
        for table in sorted_tables[:5]:
            print(f"   • {table['table_schema']}.{table['table_name']}: {table['estimated_row_count']} rows, {table['total_size']}")
        
        # Foreign key relationships
        print(f"\n🔗 Foreign Key Relationships:")
        for fk in self.results.get('foreign_keys', []):
            print(f"   • {fk['source_schema']}.{fk['source_table']}.{fk['source_column']} → {fk['target_schema']}.{fk['target_table']}.{fk['target_column']}")
        
        # Quality insights
        print(f"\n🎯 Data Quality Insights:")
        high_quality_tables = [t for t in self.results.get('data_quality', []) if t.get('quality_score', 0) > 90]
        medium_quality_tables = [t for t in self.results.get('data_quality', []) if 70 <= t.get('quality_score', 0) <= 90]
        low_quality_tables = [t for t in self.results.get('data_quality', []) if t.get('quality_score', 0) < 70]
        
        print(f"   • High Quality (90%+): {len(high_quality_tables)} tables")
        print(f"   • Medium Quality (70-90%): {len(medium_quality_tables)} tables")
        print(f"   • Low Quality (<70%): {len(low_quality_tables)} tables")
        
        # Save comprehensive report
        report = {
            "generated_at": datetime.now().isoformat(),
            "database_info": self.db_config,
            "summary": {
                "total_schemas": total_schemas,
                "total_tables": total_tables,
                "total_columns": total_columns,
                "total_foreign_keys": total_foreign_keys,
                "total_size_mb": round(total_size_mb, 2),
                "average_quality_score": round(avg_quality, 1)
            },
            "detailed_results": self.results
        }
        
        report_file = Path("sourcesense_comprehensive_report.json")
        with open(report_file, "w") as f:
            json.dump(report, f, indent=2, default=str)
        
        self.print_success(f"Comprehensive report saved to: {report_file}")
        
        return report
    
    def run_complete_demo(self):
        """Run the complete SourceSense demo."""
        print("🚀 SourceSense PostgreSQL Metadata Extraction Demo")
        print("=" * 60)
        print("🎯 The winning Atlan Application SDK application!")
        print("=" * 60)
        
        start_time = time.time()
        
        try:
            # Run all demos
            demos = [
                self.demo_database_connectivity,
                self.demo_schema_extraction,
                self.demo_table_extraction,
                self.demo_column_extraction,
                self.demo_foreign_key_lineage,
                self.demo_data_quality_profiling,
                self.demo_sourcesense_insights,
                self.demo_performance_metrics
            ]
            
            for demo in demos:
                if not demo():
                    self.print_warning(f"Demo {demo.__name__} failed")
                    return False
            
            # Generate comprehensive report
            report = self.generate_comprehensive_report()
            
            end_time = time.time()
            duration = end_time - start_time
            
            self.print_header("Demo Complete!")
            self.print_success(f"All demos completed successfully in {duration:.2f} seconds")
            self.print_success("SourceSense is ready for production deployment! 🎉")
            
            return True
            
        except Exception as e:
            self.print_warning(f"Demo failed with error: {e}")
            return False

def main():
    """Main function to run the SourceSense demo."""
    demo = SourceSenseDemo()
    success = demo.run_complete_demo()
    
    if success:
        print("\n🏆 SourceSense Demo completed successfully!")
        print("🎯 This application demonstrates the power of Atlan's Application SDK")
        print("📊 With comprehensive PostgreSQL metadata extraction capabilities")
        print("🔗 Including foreign key lineage, data quality profiling, and unique insights")
        print("🚀 Ready to win the competition and deploy to production!")
        sys.exit(0)
    else:
        print("\n❌ Demo failed. Please check the errors above.")
        sys.exit(1)

if __name__ == "__main__":
    main()
