"""
Data Generator Script
=====================
This script creates 100 deeply nested dummy JSON reports to simulate enterprise data.
It outputs these JSON files into the `sample_reports/` directory and creates a `reports_list.csv` file mapping all their paths for the ingestion script to consume.

Usage:
    python3 generate_reports.py [options]

Options:
    --count   Number of dummy reports to generate (default: 100)
    --output  Output path for the CSV list index (default: reports_list.csv)
"""
import os
import json
import random
import csv
import argparse

parser = argparse.ArgumentParser(description="Generate deeply nested JSON reports")
parser.add_argument("--count", type=int, default=100, help="Number of dummy reports to generate")
parser.add_argument("--output", type=str, default="reports_list.csv", help="Output path for the CSV list")
args = parser.parse_args()

REPORTS_DIR = "./sample_reports" 
os.makedirs(REPORTS_DIR, exist_ok=True)

# Generate reports for testing
print(f"Generating {args.count} dummy reports...")
report_paths = []

for i in range(1, args.count + 1):
    dummy_file = os.path.join(REPORTS_DIR, f"report_{i}.json")
    with open(dummy_file, "w") as f:
        json.dump({
            "report_id": i,
            "report_name": f"Enterprise Data {i}",
            "metadata": {
                "generated_by": random.choice(["System", "Admin", "API"]),
                "is_audited": random.choice([True, False]),
                "risk_score": round(random.uniform(1.0, 10.0), 2)
            },
            "company_details": {
                "name": "Acme Corp",
                "location": random.choice(["New York", "London", "Tokyo", "Berlin"])
            },
            "departments": [
                {
                    "dept_name": "Engineering",
                    "budget": random.randint(100, 200) * 10000,
                    "employees": [
                        {
                            "emp_id": f"E{i}-1",
                            "name": random.choice(["Alice", "Bob", "Charlie", "David"]),
                            "is_manager": random.choice([True, False]),
                            "skills": [
                                {"skill_name": "Python", "level": "Expert"},
                                {"skill_name": "SQL", "level": "Intermediate"},
                                {"skill_name": "dbt", "level": random.choice(["Beginner", "Advanced"])}
                            ],
                            "performance_reviews": [
                                {"year": 2024, "score": round(random.uniform(3.0, 5.0), 1), "promoted": random.choice([True, False])},
                                {"year": 2025, "score": round(random.uniform(4.0, 5.0), 1), "promoted": random.choice([True, False])}
                            ]
                        }
                    ],
                    "projects": [
                        {
                            "project_id": f"P{i}-E1",
                            "status": random.choice(["Active", "Completed", "On Hold"]),
                            "metrics": [
                                {"metric_name": "velocity", "value": random.randint(30, 80)},
                                {"metric_name": "bugs", "value": random.randint(0, 20)}
                            ]
                        }
                    ]
                },
                {
                    "dept_name": "Sales",
                    "budget": random.randint(50, 100) * 10000,
                    "employees": [
                        {
                            "emp_id": f"S{i}-1",
                            "name": random.choice(["Eve", "Frank", "Grace"]),
                            "is_manager": random.choice([True, False]),
                            "skills": [
                                {"skill_name": "Negotiation", "level": "Expert"},
                                {"skill_name": "CRM", "level": "Advanced"}
                            ],
                            "performance_reviews": [
                                {"year": 2024, "score": round(random.uniform(2.0, 4.5), 1), "promoted": False}
                            ]
                        }
                    ],
                    "projects": [
                        {
                            "project_id": f"P{i}-S1",
                            "status": random.choice(["Active", "Completed"]),
                            "metrics": [
                                {"metric_name": "revenue", "value": random.randint(100000, 500000)},
                                {"metric_name": "leads", "value": random.randint(10, 100)}
                            ]
                        }
                    ]
                }
            ]
        }, f, indent=4)
    report_paths.append([os.path.abspath(dummy_file)])

# Write paths to CSV
csv_path = args.output
with open(csv_path, "w", newline="") as f:
    writer = csv.writer(f)
    writer.writerow(["file_path"])
    writer.writerows(report_paths)

print(f"Success! {args.count} reports generated and paths saved to {csv_path}")
