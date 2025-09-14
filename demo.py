#!/usr/bin/env python3
"""
SourceSense PostgreSQL Demo Script

This script demonstrates the capabilities of SourceSense by:
1. Setting up a PostgreSQL database with sample data
2. Running the metadata extraction workflow
3. Displaying the extracted metadata and insights

Usage:
    python demo.py [--setup-only] [--extract-only] [--full-demo]
"""

import asyncio
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Dict, Any, List

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


class SourceSenseDemo:
    """SourceSense demonstration class."""
    
    def __init__(self):
        self.postgres_config = {
            'host': os.getenv('POSTGRES_HOST', 'localhost'),
            'port': os.getenv('POSTGRES_PORT', '5432'),
            'user': os.getenv('POSTGRES_USER', 'postgres'),
            'password': os.getenv('POSTGRES_PASSWORD', 'password'),
            'database': os.getenv('POSTGRES_DATABASE', 'sample_db')
        }
        self.app_config = {
            'app_name': os.getenv('APP_NAME', 'sourcesense-postgres'),
            'tenant_id': os.getenv('TENANT_ID', 'demo-tenant'),
            'connection_name': os.getenv('CONNECTION_NAME', 'demo-connection')
        }
    
    def print_header(self, title: str):
        """Print a formatted header."""
        print(f"\n{'='*60}")
        print(f"  {title}")
        print(f"{'='*60}")
    
    def print_section(self, title: str):
        """Print a formatted section header."""
        print(f"\n{'-'*40}")
        print(f"  {title}")
        print(f"{'-'*40}")
    
    def check_dependencies(self) -> bool:
        """Check if required dependencies are available."""
        self.print_section("Checking Dependencies")
        
        try:
            # Check PostgreSQL connection
            conn = psycopg2.connect(**self.postgres_config)
            conn.close()
            print("✅ PostgreSQL connection successful")
        except Exception as e:
            print(f"❌ PostgreSQL connection failed: {e}")
            return False
        
        try:
            # Check if uv is available
            result = subprocess.run(['uv', '--version'], capture_output=True, text=True)
            if result.returncode == 0:
                print(f"✅ uv available: {result.stdout.strip()}")
            else:
                print("❌ uv not available")
                return False
        except FileNotFoundError:
            print("❌ uv not found in PATH")
            return False
        
        return True
    
    def setup_database(self) -> bool:
        """Set up the PostgreSQL database with sample data."""
        self.print_section("Setting up PostgreSQL Database")
        
        try:
            # Connect to PostgreSQL
            conn = psycopg2.connect(**self.postgres_config)
            conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
            cursor = conn.cursor()
            
            # Check if database exists
            cursor.execute("SELECT 1 FROM pg_database WHERE datname = %s", (self.postgres_config['database'],))
            if not cursor.fetchone():
                print(f"Creating database: {self.postgres_config['database']}")
                cursor.execute(f"CREATE DATABASE {self.postgres_config['database']}")
            
            # Load sample data
            init_sql_path = Path(__file__).parent / "docker" / "postgres" / "init.sql"
            if init_sql_path.exists():
                print("Loading sample data...")
                with open(init_sql_path, 'r') as f:
                    sql_content = f.read()
                
                # Split by semicolon and execute each statement
                statements = [stmt.strip() for stmt in sql_content.split(';') if stmt.strip()]
                for stmt in statements:
                    if stmt:
                        try:
                            cursor.execute(stmt)
                        except Exception as e:
                            print(f"Warning: {e}")
                
                print("✅ Sample data loaded successfully")
            else:
                print("❌ Sample data file not found")
                return False
            
            cursor.close()
            conn.close()
            return True
            
        except Exception as e:
            print(f"❌ Database setup failed: {e}")
            return False
    
    def run_metadata_extraction(self) -> bool:
        """Run the metadata extraction workflow."""
        self.print_section("Running Metadata Extraction")
        
        try:
            # Start the application
            print("Starting SourceSense application...")
            process = subprocess.Popen(
                ['uv', 'run', 'main.py'],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True
            )
            
            # Wait for application to start
            print("Waiting for application to start...")
            time.sleep(10)
            
            # Check if process is still running
            if process.poll() is not None:
                stdout, stderr = process.communicate()
                print(f"❌ Application failed to start:")
                print(f"STDOUT: {stdout}")
                print(f"STDERR: {stderr}")
                return False
            
            print("✅ Application started successfully")
            print("📊 Metadata extraction workflow is running...")
            print("🌐 Web interface available at: http://localhost:8000")
            print("⏱️  Temporal UI available at: http://localhost:8233")
            
            # Keep running for demo
            print("\nPress Ctrl+C to stop the application...")
            try:
                process.wait()
            except KeyboardInterrupt:
                print("\n🛑 Stopping application...")
                process.terminate()
                process.wait()
            
            return True
            
        except Exception as e:
            print(f"❌ Metadata extraction failed: {e}")
            return False
    
    def analyze_database(self) -> Dict[str, Any]:
        """Analyze the database and return metadata insights."""
        self.print_section("Database Analysis")
        
        try:
            conn = psycopg2.connect(**self.postgres_config)
            cursor = conn.cursor()
            
            # Get database statistics
            cursor.execute("""
                SELECT 
                    datname as database_name,
                    pg_size_pretty(pg_database_size(datname)) as size,
                    (SELECT COUNT(*) FROM pg_stat_activity WHERE datname = current_database()) as connections
                FROM pg_database 
                WHERE datname = current_database()
            """)
            db_info = cursor.fetchone()
            
            # Get schema information
            cursor.execute("""
                SELECT 
                    schema_name,
                    (SELECT COUNT(*) FROM information_schema.tables WHERE table_schema = s.schema_name) as table_count,
                    (SELECT COUNT(*) FROM information_schema.views WHERE table_schema = s.schema_name) as view_count
                FROM information_schema.schemata s
                WHERE schema_name NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
                ORDER BY schema_name
            """)
            schemas = cursor.fetchall()
            
            # Get table information
            cursor.execute("""
                SELECT 
                    table_schema,
                    table_name,
                    table_type,
                    (SELECT COUNT(*) FROM information_schema.columns WHERE table_schema = t.table_schema AND table_name = t.table_name) as column_count
                FROM information_schema.tables t
                WHERE table_schema NOT IN ('information_schema', 'pg_catalog', 'pg_toast')
                ORDER BY table_schema, table_name
            """)
            tables = cursor.fetchall()
            
            # Get foreign key relationships
            cursor.execute("""
                SELECT 
                    tc.table_schema as source_schema,
                    tc.table_name as source_table,
                    ccu.table_schema as target_schema,
                    ccu.table_name as target_table,
                    tc.constraint_name
                FROM information_schema.table_constraints tc
                JOIN information_schema.constraint_column_usage ccu ON tc.constraint_name = ccu.constraint_name
                WHERE tc.constraint_type = 'FOREIGN KEY'
                ORDER BY tc.table_schema, tc.table_name
            """)
            foreign_keys = cursor.fetchall()
            
            cursor.close()
            conn.close()
            
            return {
                'database': db_info,
                'schemas': schemas,
                'tables': tables,
                'foreign_keys': foreign_keys
            }
            
        except Exception as e:
            print(f"❌ Database analysis failed: {e}")
            return {}
    
    def display_insights(self, analysis: Dict[str, Any]):
        """Display database insights and metadata."""
        self.print_section("Database Insights")
        
        if not analysis:
            print("❌ No analysis data available")
            return
        
        # Database information
        if analysis.get('database'):
            db_name, size, connections = analysis['database']
            print(f"📊 Database: {db_name}")
            print(f"💾 Size: {size}")
            print(f"🔗 Active Connections: {connections}")
        
        # Schema information
        if analysis.get('schemas'):
            print(f"\n📁 Schemas ({len(analysis['schemas'])}):")
            for schema_name, table_count, view_count in analysis['schemas']:
                print(f"  • {schema_name}: {table_count} tables, {view_count} views")
        
        # Table information
        if analysis.get('tables'):
            print(f"\n🗃️  Tables ({len(analysis['tables'])}):")
            for schema, table, table_type, column_count in analysis['tables']:
                print(f"  • {schema}.{table} ({table_type}): {column_count} columns")
        
        # Foreign key relationships
        if analysis.get('foreign_keys'):
            print(f"\n🔗 Foreign Key Relationships ({len(analysis['foreign_keys'])}):")
            for source_schema, source_table, target_schema, target_table, constraint in analysis['foreign_keys']:
                print(f"  • {source_schema}.{source_table} → {target_schema}.{target_table} ({constraint})")
    
    def run_full_demo(self):
        """Run the complete demonstration."""
        self.print_header("SourceSense PostgreSQL Demo")
        
        print("🚀 Welcome to SourceSense - Intelligent PostgreSQL Metadata Extraction")
        print("This demo will showcase advanced metadata extraction capabilities.")
        
        # Check dependencies
        if not self.check_dependencies():
            print("❌ Dependency check failed. Please install required dependencies.")
            return False
        
        # Setup database
        if not self.setup_database():
            print("❌ Database setup failed.")
            return False
        
        # Analyze database
        analysis = self.analyze_database()
        self.display_insights(analysis)
        
        # Run metadata extraction
        if not self.run_metadata_extraction():
            print("❌ Metadata extraction failed.")
            return False
        
        self.print_header("Demo Complete!")
        print("✅ SourceSense has successfully demonstrated:")
        print("  • PostgreSQL database connection and analysis")
        print("  • Comprehensive metadata extraction")
        print("  • Foreign key lineage mapping")
        print("  • Data quality profiling")
        print("  • Business context enrichment")
        
        return True


def main():
    """Main entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='SourceSense PostgreSQL Demo')
    parser.add_argument('--setup-only', action='store_true', help='Only setup the database')
    parser.add_argument('--extract-only', action='store_true', help='Only run metadata extraction')
    parser.add_argument('--full-demo', action='store_true', help='Run the complete demo')
    
    args = parser.parse_args()
    
    demo = SourceSenseDemo()
    
    if args.setup_only:
        demo.print_header("Database Setup Only")
        demo.check_dependencies()
        demo.setup_database()
    elif args.extract_only:
        demo.print_header("Metadata Extraction Only")
        demo.check_dependencies()
        demo.run_metadata_extraction()
    else:
        # Default to full demo
        demo.run_full_demo()


if __name__ == '__main__':
    main()

