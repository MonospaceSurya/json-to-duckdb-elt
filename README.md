# 🦆 Nested JSON to DuckDB/SQLite Pipeline

[![dlt](https://img.shields.io/badge/ingestion-dlt-blue.svg)](https://dlthub.com/)
[![dbt](https://img.shields.io/badge/transformation-dbt-orange.svg)](https://www.getdbt.com/)
[![duckdb](https://img.shields.io/badge/database-DuckDB-yellow.svg)](https://duckdb.org/)

An automated, end-to-end Extract, Load, and Transform (ELT) pipeline designed to ingest deeply nested, highly complex JSON reports and flatten them into beautiful analytical tables. 

Perfect for feeding BI tools like Metabase or Apache Superset!

---

## 📖 Table of Contents
1. [File Structure](#-file-structure)
2. [Architecture Overview](#-architecture-overview)
3. [Prerequisites](#-prerequisites)
4. [Quickstart Guide](#-quickstart-guide)
5. [Changing the Database Engine](#-changing-the-database-engine)

---

## 📂 File Structure

```text
json-to-duckdb-elt/
│
├── generate_reports.py      # Generates dummy data
├── 1_extract_load.py        # Ingests JSON into DuckDB/SQLite
├── 2_transform.py           # Runs dbt models
├── 3_document.py            # Generates markdown documentation
│
├── db/                      # Output directory for databases (.duckdb / .db)
├── docs/                    # Output directory for schema documentation
├── sample_reports/          # Folder containing raw generated JSON
│
└── analytics_transform/     # The dbt project folder
    ├── dbt_project.yml
    ├── profiles.yml         # Configured for both duckdb & sqlite
    └── models/              # Contains the flattening SQL logic
```

---

## 🏗️ Architecture Overview

Handling JSON with 4-layer deep nested lists (e.g., `departments` -> `employees` -> `skills`) is a massive pain in standard SQL. This project solves that elegantly in three steps:

1. **Ingest (`dlt`)**: The `dlt` Python library reads the chaotic JSON and automatically normalizes it into a highly relational schema, auto-generating Primary Keys (`_dlt_id`) and Foreign Keys (`_dlt_parent_id`).
2. **Transform (`dbt`)**: `dbt` runs complex `JOIN` models to re-flatten the data into wide, analytical tables (e.g., `analytics_employee_performance`).
3. **Document**: A custom Python script connects to the `information_schema` and auto-generates a gorgeous Markdown schema mapping for developers.

---

## ⚙️ Prerequisites

You will need Python 3.9+ and the following packages:

```bash
# Install core ingestion tools
pip install dlt[duckdb] dlt[sqlite]

# Install transformation tools
pip install dbt-core dbt-duckdb dbt-sqlite

# Install python DB API for duckdb
pip install duckdb
```

---

## 🚀 Quickstart Guide

This project is completely self-contained. Follow these steps to generate data, build the database, and create the documentation.

### 1. Generate Dummy Data
```bash
python3 generate_reports.py --count 100 --output reports_list.csv
```
*Creates 100 heavily nested JSON files in `./sample_reports/` and maps their absolute paths to `reports_list.csv`.*

### 2. Extract & Load
```bash
python3 1_extract_load.py --csv reports_list.csv --engine duckdb --pipeline_name my_pipeline --db_path ./db/my_pipeline.duckdb
```
*Reads the CSV, infers the massive JSON schema, and loads it into a `.duckdb` (or `.db`) file. The `--pipeline_name` controls the internal name of the `dlt` ingestion pipeline, and acts as the default database name if `--db_path` is omitted.*

### 3. Transform
```bash
python3 2_transform.py --target dev_duckdb --dbt_project_dir analytics_transform --db_path ./db/my_pipeline.duckdb
```
*Triggers `dbt run` behind the scenes. This compiles the raw normalized tables into flattened analytics views!*

### 4. Document
```bash
python3 3_document.py --engine duckdb --pipeline_name my_pipeline --db_path ./db/my_pipeline.duckdb --docs_dir docs
```
*Scans the final database and outputs `database_schema.md` inside the specified docs directory.*

---

## 🔄 Changing the Database Engine

This project supports a **Dual-Engine Architecture**. You can seamlessly swap between **DuckDB** (for blazing fast analytics) and **SQLite** (for simple lightweight apps) simply by passing arguments to the CLI!

To switch to SQLite, just append the following flags to your commands:
1. `python3 1_extract_load.py --engine sqlite --db_path ./db/custom.db`
2. `python3 2_transform.py --target dev_sqlite --db_path ./db/custom.db`
3. `python3 3_document.py --engine sqlite --db_path ./db/custom.db`
