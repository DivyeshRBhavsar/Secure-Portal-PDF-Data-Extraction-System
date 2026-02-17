# src/csv_writer.py
import csv
import os


def append_to_csv_schema(csv_path, data, fieldnames, key_field="policy_number"):
    """
    Inserts or updates a row in the CSV based on a unique key field.
    Default key field = policy_number.
    """

    rows = []

    # ✅ Load existing data if file exists
    if os.path.exists(csv_path):
        with open(csv_path, newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            rows = list(reader)

    # ✅ Remove existing record with same key
    rows = [
        row for row in rows
        if row.get(key_field) != str(data.get(key_field))
    ]

    # ✅ Add updated row
    new_row = {field: data.get(field, "") for field in fieldnames}
    rows.append(new_row)

    # ✅ Rewrite entire file
    with open(csv_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)