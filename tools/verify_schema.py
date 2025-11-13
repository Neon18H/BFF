#!/usr/bin/env python3
"""Validate that Supabase schema matches Flutter models."""

from __future__ import annotations

import re
import sys
from pathlib import Path
from typing import List, Set

ROOT = Path(__file__).resolve().parents[1]
MIGRATIONS = ROOT / "migrations" / "001_init.sql"
CLIENTS_MODEL = ROOT.parent / "lib" / "clients" / "models" / "models.dart"
TASKS_MODEL = ROOT.parent / "lib" / "tasks" / "models" / "task.dart"


def camel_to_snake(name: str) -> str:
    return re.sub(r"(?<!^)(?=[A-Z])", "_", name).lower()


def extract_table_columns(sql: str, table: str) -> Set[str]:
    pattern = re.compile(rf"create table\s+public\.{table}\s*\((.*?)\);", re.IGNORECASE | re.DOTALL)
    match = pattern.search(sql)
    if not match:
        raise SystemExit(f"Table {table} not found in migrations")
    body = match.group(1)
    columns = set()
    for line in body.splitlines():
        line = line.strip()
        if not line or line.startswith("--"):
            continue
        column = line.split()[0]
        column = column.strip('"')
        if column.lower() in {"constraint", "primary", "foreign", "unique"}:
            continue
        columns.add(column)
    return columns


def extract_class_fields(path: Path, class_name: str) -> List[str]:
    fields: List[str] = []
    lines = path.read_text(encoding="utf-8").splitlines()
    inside = False
    depth = 0
    for line in lines:
        stripped = line.strip()
        if not inside and stripped.startswith(f"class {class_name}"):
            inside = True
            depth += stripped.count("{") - stripped.count("}")
            continue
        if inside:
            depth += stripped.count("{") - stripped.count("}")
            if stripped.startswith("final ") and "=" not in stripped:
                parts = stripped.split()
                if len(parts) >= 3:
                    fields.append(parts[2].rstrip(';'))
            if depth <= 0:
                break
    if not fields:
        raise SystemExit(f"No fields found for class {class_name} in {path}")
    return fields


def validate_mapping(columns: Set[str], fields: List[str], table: str) -> List[str]:
    missing = []
    for field in fields:
        column = camel_to_snake(field)
        if column not in columns:
            missing.append(f"{table}.{column}")
    return missing


def main() -> int:
    sql = MIGRATIONS.read_text(encoding="utf-8")
    clients_columns = extract_table_columns(sql, "clients")
    tasks_columns = extract_table_columns(sql, "tasks")

    client_fields = extract_class_fields(CLIENTS_MODEL, "Client")
    task_fields = extract_class_fields(TASKS_MODEL, "Task")

    missing = []
    missing.extend(validate_mapping(clients_columns, client_fields, "clients"))
    missing.extend(validate_mapping(tasks_columns, task_fields, "tasks"))

    if missing:
        print("Schema mismatch detected for columns:")
        for item in missing:
            print(f" - {item}")
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
