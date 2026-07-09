# 🦆 Nested JSON to DuckDB/SQLite Pipeline

[![dlt](https://img.shields.io/badge/ingestion-dlt-blue.svg)](https://dlthub.com/)
[![dbt](https://img.shields.io/badge/transformation-dbt-orange.svg)](https://www.getdbt.com/)
[![duckdb](https://img.shields.io/badge/database-DuckDB-yellow.svg)](https://duckdb.org/)
[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![Open Source Love](https://badges.frapsoft.com/os/v1/open-source.svg?v=103)](https://github.com/ellerbrock/open-source-badges/)

An automated, end-to-end Extract, Load, and Transform (ELT) pipeline designed to ingest deeply nested, highly complex JSON reports and flatten them into beautiful analytical tables. 

Perfect for feeding BI tools like Metabase or Apache Superset!

> **⭐️ If you find this project useful, please consider giving it a star on GitHub! It helps others discover the project.**

---

## 📖 Table of Contents
1. [File Structure](#-file-structure)
2. [Architecture Overview](#-architecture-overview)
3. [Prerequisites](#-prerequisites)
4. [Quickstart Guide](#-quickstart-guide)
5. [Customizing for Your Own Data](#-customizing-for-your-own-data)
6. [Changing the Database Engine](#-changing-the-database-engine)

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

### 🛑 The Problem

Want to run blazingly fast analytical queries across fields in deeply nested JSON? 

Your first instinct might be to dump it all into MongoDB or another NoSQL database. But here is the catch: **NoSQL databases are built for transactional application state, not for heavy analytical aggregations.** 

If you want to use a Business Intelligence (BI) tool like **Metabase** or **Apache Superset** to create beautiful dashboards, they expect clean, structured, flat relational tables. They do not know how to handle chaotic JSON.

Take a look at this sample JSON:

```json
{
  "event_id": "evt_987654321",
  "timestamp": "2023-10-27T14:32:00Z",
  "metadata": {
    "source_system": "mobile_app",
    "region": "US-West"
  },
  "payload": {
    "user": {
      "id": "u_123",
      "session_history": [
        {"login_time": "08:00", "device": "iOS"},
        {"login_time": "14:00", "device": "Web"}
      ]
    },
    "purchases": [
      {
        "transaction_id": "tx_001",
        "items": [
          {"product_id": "p_99", "price": 49.99, "tags": ["electronics", "sale"]},
          {"product_id": "p_42", "price": 9.99, "tags": ["accessories"]}
        ]
      }
    ]
  }
}
```

How do you write a SQL query to find the *average revenue per user by region* when the data is buried 4 layers deep inside lists of lists? 

Now, ask yourself: **What if you have 100 million of these JSON files?** Writing complex cross-field JSON extraction queries on the fly becomes computationally impossible.

### 💡 The Solution
To bring strict relational structure to our JSON, we perform this 3-step pipeline:

1. **Ingest (`dlt`)**: The `dlt` Python library reads the chaotic JSON and automatically normalizes it into a highly relational schema. It auto-generates Primary Keys (`_dlt_id`) and Foreign Keys (`_dlt_parent_id`), stripping away the nesting.
2. **Transform (`dbt`)**: `dbt` runs complex `JOIN` models to re-flatten the normalized data into wide, analytical tables (e.g., `analytics_employee_performance`) that are perfectly optimized for BI aggregation.
3. **Document**: A custom Python script connects to the `information_schema` and auto-generates a gorgeous Markdown schema mapping for developers.

### Why DuckDB?
DuckDB is an insanely fast, in-process analytical database. It can effortlessly chew through **500 million rows** on a standard laptop, making it the perfect engine for powering blazing-fast BI dashboards without the overhead of managing a traditional cloud data warehouse!

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

## 🛠️ Customizing for Your Own Data

Want to run this pipeline on your own chaotic JSON files? It's incredibly easy because the ingestion script **dynamically infers your schema**. You don't need to write a single line of Python to parse your custom JSON!

Here is exactly how to adapt the project for your own workflow:

1. **Provide Your Own CSV:**
   Instead of using the dummy data generator, simply create a CSV file (e.g., `my_custom_reports.csv`) that contains a single column listing the absolute file paths to your own JSON files. It should look like this:
   ```csv
   file_path
   /Users/data/json_exports/report_2023.json
   /Users/data/json_exports/report_2024.json
   ...
   ```
2. **Run the Extractor:**
   Run the ingestion script pointing to your CSV:
   ```bash
   python3 1_extract_load.py --csv my_custom_reports.csv --pipeline_name my_custom_data
   ```
   *The `dlt` engine will automatically map out every array and nested object in your JSON files and generate the relational DuckDB tables.*
3. **Write Your Custom SQL:**
   Open the `analytics_transform/models/` folder. Delete the demo SQL files and write your own `dbt` models using standard SQL `JOIN`s to flatten your specific data. (Tip: Run `3_document.py` first to generate a Markdown schema so you know exactly what tables and Foreign Keys `dlt` created for you!)
4. **Transform:**
   Run the transform script to compile your new custom models into your database!
   ```bash
   python3 2_transform.py --target dev_duckdb --dbt_project_dir analytics_transform --db_path ./db/my_custom_data.duckdb
   ```

---

## 🔄 Changing the Database Engine

This project supports a **Dual-Engine Architecture**. You can seamlessly swap between **DuckDB** (for blazing fast analytics) and **SQLite** (for simple lightweight apps) simply by passing arguments to the CLI!

To switch to SQLite, just append the following flags to your commands:
1. `python3 1_extract_load.py --engine sqlite --db_path ./db/custom.db`
2. `python3 2_transform.py --target dev_sqlite --db_path ./db/custom.db`
3. `python3 3_document.py --engine sqlite --db_path ./db/custom.db`
