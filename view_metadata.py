#!/usr/bin/env python3
"""
Script to view the extracted metadata from the workflow.
"""

import pandas as pd
import os
import json

def view_metadata():
    """View the extracted metadata from the latest workflow run."""
    
    # Path to the latest workflow output
    workflow_path = "./local/tmp/artifacts/apps/sourcesense-postgres/workflows/cd2c5130-2308-4c05-8b5e-5c3faa005d11/01994849-b794-7766-b2e6-8409215188fc/raw"
    
    print("🔍 SourceSense Metadata Extraction Results")
    print("=" * 60)
    
    # View each type of metadata
    metadata_types = ['database', 'schema', 'table', 'column', 'foreign_keys', 'data_quality']
    
    for metadata_type in metadata_types:
        type_path = os.path.join(workflow_path, metadata_type)
        if os.path.exists(type_path):
            print(f"\n📊 {metadata_type.upper()} METADATA:")
            print("-" * 40)
            
            # List all files in this directory
            files = [f for f in os.listdir(type_path) if f.endswith('.parquet')]
            
            for file in files:
                file_path = os.path.join(type_path, file)
                try:
                    # Read the parquet file
                    df = pd.read_parquet(file_path)
                    print(f"  📁 {file}: {len(df)} records")
                    
                    # Show column names
                    print(f"     Columns: {', '.join(df.columns.tolist())}")
                    
                    # Show first few rows for small datasets
                    if len(df) <= 10:
                        print("     Sample data:")
                        for idx, row in df.head(3).iterrows():
                            print(f"       {dict(row)}")
                    else:
                        print(f"     First 3 records:")
                        for idx, row in df.head(3).iterrows():
                            print(f"       {dict(row)}")
                    
                    print()
                    
                except Exception as e:
                    print(f"     Error reading {file}: {e}")
        else:
            print(f"\n❌ {metadata_type.upper()}: No data found")

if __name__ == "__main__":
    view_metadata()
