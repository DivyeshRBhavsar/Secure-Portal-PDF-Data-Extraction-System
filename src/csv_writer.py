# src/csv_writer.py
import csv
import os

def append_to_csv_schema(csv_path, data, fieldnames):
    file_exists = os.path.exists(csv_path)

    with open(csv_path, "a", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)

        if not file_exists:
            writer.writeheader()

        row = {field: data.get(field, "") for field in fieldnames}
        writer.writerow(row)