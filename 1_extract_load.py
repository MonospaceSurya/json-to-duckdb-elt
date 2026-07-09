"""
Step 1: Extract & Load (dlt)
============================
This script generates deeply nested dummy JSON reports and ingests them into a SQLite database using the `dlt` library.
It automatically flattens nested arrays into relational tables and handles all schema inference.

Usage:
    python3 1_extract_load.py [options]

Options:
    --csv            Path to the CSV index of JSON files (default: reports_list.csv)
    --engine         Target database engine (duckdb or sqlite, default: duckdb)
    --pipeline_name  The internal name of the dlt ingestion pipeline, which also dictates the default output database filename if --db_path is not specified (default: my_pipeline)
    --db_path        Explicit path to output the database file

Requirements:
    pip3 install dlt[duckdb] dlt[sqlite]
"""
import dlt
import json
import os
import csv
# import glob
# import random

import argparse

parser = argparse.ArgumentParser(description="Extract and Load JSON to Database")
parser.add_argument("--csv", type=str, default="reports_list.csv", help="Path to the CSV containing JSON file paths")
parser.add_argument("--engine", type=str, default="duckdb", choices=["duckdb", "sqlite"], help="Target database engine")
parser.add_argument("--db_path", type=str, default=None, help="Path to output the database file")
parser.add_argument("--pipeline_name", type=str, default="my_pipeline", help="Name of the dlt pipeline")
args = parser.parse_args()

# 1. Configuration
DESTINATION = args.engine
CSV_PATH = args.csv
PIPELINE_NAME = args.pipeline_name

# Determine the final DB path
if args.db_path:
    final_db_path = os.path.abspath(args.db_path)
    output_dir = os.path.dirname(final_db_path)
    os.makedirs(output_dir, exist_ok=True)
else:
    output_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "db")
    os.makedirs(output_dir, exist_ok=True)
    extension = ".duckdb" if DESTINATION == "duckdb" else ".db"
    final_db_path = os.path.join(output_dir, f"{PIPELINE_NAME}{extension}")

# Define where the data goes
if DESTINATION == "duckdb":
    duckdb_path = final_db_path
    pipeline = dlt.pipeline(
        pipeline_name=PIPELINE_NAME,
        destination=dlt.destinations.duckdb(credentials=duckdb_path),
        dataset_name="main"
    )
elif DESTINATION == "sqlite":
    sqlite_path = f"sqlite:///{final_db_path}"
    pipeline = dlt.pipeline(
        pipeline_name=PIPELINE_NAME,
        destination=dlt.destinations.sqlalchemy(credentials=sqlite_path),
        dataset_name="exploded_reports"
    )
else:
    raise ValueError("Invalid DESTINATION. Choose 'duckdb' or 'sqlite'.")

# 2. Define the generator to yield data from the CSV list of files
@dlt.resource(name="raw_reports", write_disposition="append")
def load_json_files(csv_path=CSV_PATH):
    if not os.path.exists(csv_path):
        print(f"Error: Could not find {csv_path}. Please run generate_reports.py first.")
        return
        
    with open(csv_path, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            file_path = row["file_path"]
            with open(file_path, "r") as json_f:
                data = json.load(json_f)
                
                if isinstance(data, list):
                    yield data
                else:
                    yield [data]

print("Starting pipeline run...")
load_info = pipeline.run(
    load_json_files(),
    table_name="main_report"
)

print("\n--- Load Info ---")
print(load_info)

# 4. Clean up SQLite file names and build analytical views!
if DESTINATION == "sqlite":
    original_db = final_db_path
    attached_db = os.path.join(output_dir, f"{PIPELINE_NAME}__{pipeline.dataset_name}.db")
    if os.path.exists(attached_db):
        if os.path.exists(original_db):
            os.remove(original_db)
        os.rename(attached_db, original_db)

# 5. Export schemas (Markdown for reading, YAML for dlt)
schema_md_path = os.path.join(output_dir, "database_schema.md")
schema_yaml_path = os.path.join(output_dir, "database_schema.yaml")

with open(schema_yaml_path, "w") as f:
    f.write(pipeline.default_schema.to_pretty_yaml())
print(f"Exported dlt YAML schema to: {schema_yaml_path}")



print("\n--- Pipeline successfully ran! ---")
if DESTINATION == "duckdb":
    print(f"Your DuckDB database is located at: {final_db_path}")
elif DESTINATION == "sqlite":
    print(f"Your SQLite database is located at: {final_db_path}")

print("\n--- Table Summary for dbt sources.yml ---")
print("Include the following tables in your sources.yml file:")
for table_name in pipeline.default_schema.tables.keys():
    if not table_name.startswith("_dlt"):
        print(f"      - name: {table_name}")

