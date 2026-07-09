"""
Step 3: Document (Schema Generation)
====================================
This script connects to the final database (DuckDB or SQLite) and auto-generates a Markdown file mapping the entire schema.
It includes both the raw `dlt` tables and the flattened `dbt` analytical tables, complete with row counts and inferred foreign keys.

Usage:
    python3 3_document.py [options]

Options:
    --engine         Target database engine (duckdb or sqlite, default: duckdb)
    --db_path        Explicit path to the database file
    --pipeline_name  The name of the pipeline used to build the database, which dictates the default database filename if --db_path is not specified (default: my_pipeline)
    --docs_dir       Output directory for documentation (default: docs)
"""
import duckdb
import sqlite3
import os
import argparse

parser = argparse.ArgumentParser(description="Generate markdown documentation for the database schema")
parser.add_argument("--engine", type=str, default="duckdb", choices=["duckdb", "sqlite"], help="Target database engine")
parser.add_argument("--db_path", type=str, default=None, help="Path to the database file")
parser.add_argument("--pipeline_name", type=str, default="my_pipeline", help="Name of the pipeline (used if db_path is not provided)")
parser.add_argument("--docs_dir", type=str, default="docs", help="Output directory for documentation")
args = parser.parse_args()

# 1. Configuration
ENGINE = args.engine
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

if args.db_path:
    db_path = os.path.abspath(args.db_path)
else:
    if ENGINE == "duckdb":
        db_path = os.path.join(BASE_DIR, "db", f"{args.pipeline_name}.duckdb")
    else:
        db_path = os.path.join(BASE_DIR, "db", f"{args.pipeline_name}.db")

docs_dir = os.path.abspath(args.docs_dir)
os.makedirs(docs_dir, exist_ok=True)
output_md = os.path.join(docs_dir, "database_schema.md")

if not os.path.exists(db_path):
    print(f"Error: Database not found at {db_path}")
    exit(1)

if ENGINE == "duckdb":
    conn = duckdb.connect(db_path)
    tables_df = conn.execute("SELECT table_name FROM information_schema.tables WHERE table_schema='main' ORDER BY table_name").fetchall()
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name;")
    tables_df = cursor.fetchall()

with open(output_md, "w") as f:
    f.write("# Final Analytics Database Schema\n\n")
    f.write("This file contains the complete schema of the database after both `dlt` ingestion and `dbt` transformations.\n\n")
    
    for (table_name,) in tables_df:
        # Skip internal dlt/dbt tables to keep it clean
        if table_name.startswith("_dlt") or table_name.startswith("dbt_") or table_name == "sqlite_sequence":
            continue
            
        # Get Row Count
        if ENGINE == "duckdb":
            row_count = conn.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
        else:
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            row_count = cursor.fetchone()[0]
        
        f.write(f"## Table: `{table_name}`\n")
        f.write(f"**Total Rows:** {row_count}\n\n")
        
        # dlt does not create physical foreign keys by default, so we infer them by naming convention!
        fk_map = {}
        
        # Get columns
        if ENGINE == "duckdb":
            columns = conn.execute(f"SELECT column_name, data_type, is_nullable FROM information_schema.columns WHERE table_name='{table_name}' ORDER BY ordinal_position").fetchall()
        else:
            cursor.execute(f"PRAGMA table_info({table_name});")
            # PRAGMA format: (cid, name, type, notnull, dflt_value, pk)
            columns = [(row[1], row[2], 'YES' if row[3] == 0 else 'NO') for row in cursor.fetchall()]

        column_names = [c[0] for c in columns]
        
        if "_dlt_parent_id" in column_names:
            # The parent table is simply the current table name minus the last '__' segment
            if "__" in table_name:
                parent_table = table_name.rsplit("__", 1)[0]
                fk_map["_dlt_parent_id"] = f"→ `{parent_table}`.`_dlt_id`"
            
        f.write("| Column Name | Data Type | Nullable | Primary Key | Foreign Key |\n")
        f.write("|-------------|-----------|----------|-------------|-------------|\n")
        
        for col_name, data_type, is_nullable in columns:
            nullable = "True" if is_nullable == 'YES' else "False"
            
            # In dlt, _dlt_id is the logical primary key
            is_pk = "Yes" if col_name == "_dlt_id" else "No"
            
            # In dbt views, we added report_id manually, but it's not a strict PK. We leave it as No.
            fk_info = fk_map.get(col_name, "")
            
            f.write(f"| `{col_name}` | {data_type} | {nullable} | {is_pk} | {fk_info} |\n")
        f.write("\n")

conn.close()
print(f"Successfully generated full schema at: {output_md}")
