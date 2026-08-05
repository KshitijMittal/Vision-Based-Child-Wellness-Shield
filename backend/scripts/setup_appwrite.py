#!/usr/bin/env python3
"""Provision the Appwrite Cloud schema for the Wellness Shield backend.

Idempotent — safe to run repeatedly. Creates the database, the
screening_documents table, its columns and indexes, then verifies the
result against the definitions in backend/schema.md.

Usage:
    .venv/Scripts/python.exe backend/scripts/setup_appwrite.py
"""

from __future__ import annotations

import os
import sys
import uuid
from datetime import datetime, timezone
from pathlib import Path

from dotenv import load_dotenv

from appwrite.client import Client
from appwrite.enums.order_by import OrderBy
from appwrite.enums.tables_db_index_type import TablesDBIndexType
from appwrite.permission import Permission
from appwrite.query import Query
from appwrite.role import Role
from appwrite.services.tables_db import TablesDB

BACKEND_DIR = Path(__file__).resolve().parents[1]
load_dotenv(BACKEND_DIR / ".env")

ENDPOINT = os.getenv("APPWRITE_ENDPOINT", "https://cloud.appwrite.io/v1")
PROJECT_ID = os.getenv("APPWRITE_PROJECT_ID")
API_KEY = os.getenv("APPWRITE_API_KEY")
DATABASE_ID = os.getenv("APPWRITE_DATABASE_ID", "main")
TABLE_ID = os.getenv("APPWRITE_TABLE_ID", "screening_documents")

SYMPTOMS = ["jaundice", "pallor", "skin", "goitre", "malnutrition"]
SYMPTOM_STATUS = ["not_detected", "low_confidence", "detected", "not_assessed"]
SEX_VALUES = ["boy", "girl"]
WHO_CATEGORIES = [
    "severely_underweight",
    "underweight",
    "normal",
    "overweight",
    "obese",
]
CAPTURE_QUALITY = ["good", "low"]

# (key, type, options) — types map 1:1 to the TablesDB column creators.
# Text columns (create_text_column) are the current API — the legacy
# create_string_column is deprecated since 1.9.0.
_COLUMN_SPECS: list[tuple[str, str, dict]] = [
    # --- Block A: Meta & Identification ---
    ("account_id", "text", {"required": True}),
    ("child_name", "text", {"required": True}),
    ("child_age_years", "integer", {"required": True}),
    ("child_age_months", "integer", {"required": True}),
    ("child_sex", "enum", {"elements": SEX_VALUES, "required": True}),
    ("village", "text", {"required": False}),
    ("consent_given", "boolean", {"required": True}),
    ("consent_timestamp", "datetime", {"required": True}),
    ("analysis_timestamp", "datetime", {"required": True}),
    ("created_at", "datetime", {"required": True}),
    ("updated_at", "datetime", {"required": True}),
    # --- Block B: Measurements & BMI ---
    ("estimated_height_cm", "float", {"required": True}),
    ("confirmed_weight_kg", "float", {"required": True}),
    ("bmi", "float", {"required": True}),
    ("who_percentile", "float", {"required": True}),
    ("who_category", "enum", {"elements": WHO_CATEGORIES, "required": True}),
    ("who_chart_version", "text", {"required": True}),
    # --- Block C: Symptom detection (5 symptoms x 3 fields) ---
]
for symptom in SYMPTOMS:
    _COLUMN_SPECS.append(
        (f"symptom_{symptom}_status", "enum", {"elements": SYMPTOM_STATUS, "required": True})
    )
    _COLUMN_SPECS.append((f"symptom_{symptom}_confidence", "float", {"required": True}))
    _COLUMN_SPECS.append((f"symptom_{symptom}_model_ver", "text", {"required": True}))

# --- Block D: Storage & Sync (cloud fields only) ---
_COLUMN_SPECS.append(("pdf_file_id", "text", {"required": False}))
_COLUMN_SPECS.append(("capture_quality", "enum", {"elements": CAPTURE_QUALITY, "required": True}))

# (key, columns, orders, lengths) — mapped to create_index.
# Text columns need explicit prefix lengths: 191 chars = 767-byte index limit
# ÷ 4 bytes/char (utf8mb4). Datetime columns need no length.
_INDEX_SPECS = [
    ("by_account", ["account_id", "created_at"], [OrderBy.ASC, OrderBy.DESC], [191]),
    (
        "by_account_name",
        ["account_id", "child_name", "created_at"],
        [OrderBy.ASC, OrderBy.ASC, OrderBy.DESC],
        [191, 191],
    ),
    ("by_created_at", ["created_at"], [OrderBy.ASC], []),
]

# Table is sealed per-row: any logged-in user may create, and each row carries
# user:{account_id} permissions (Backend Schema §8.1). No table-level read.
_TABLE_PERMISSIONS = [Permission.create(Role.users())]


def _get_client() -> Client:
    if not PROJECT_ID or not API_KEY:
        sys.exit("APPWRITE_PROJECT_ID and APPWRITE_API_KEY must be set in backend/.env")

    client = Client()
    client.set_endpoint(ENDPOINT)
    client.set_project(PROJECT_ID)
    client.set_key(API_KEY)
    return client


def _ensure_database(db: TablesDB) -> None:
    known = {d.id for d in db.list().databases}
    if DATABASE_ID in known:
        print(f"database '{DATABASE_ID}' exists")
        return
    db.create(DATABASE_ID, DATABASE_ID)
    print(f"database '{DATABASE_ID}' created")


def _ensure_table(db: TablesDB) -> None:
    known = {t.id for t in db.list_tables(DATABASE_ID).tables}
    if TABLE_ID in known:
        print(f"table '{TABLE_ID}' exists")
        return
    db.create_table(
        DATABASE_ID,
        TABLE_ID,
        TABLE_ID,
        permissions=_TABLE_PERMISSIONS,
        row_security=True,
    )
    print(f"table '{TABLE_ID}' created (row_security on)")


def _ensure_columns(db: TablesDB) -> None:
    # list_* defaults to 25 results per page; the schema exceeds that.
    existing = {
        c.key
        for c in db.list_columns(DATABASE_ID, TABLE_ID, queries=[Query.limit(100)]).columns
    }
    for key, kind, opts in _COLUMN_SPECS:
        if key in existing:
            continue
        if kind == "text":
            db.create_text_column(DATABASE_ID, TABLE_ID, key, required=opts["required"])
        elif kind == "integer":
            db.create_integer_column(DATABASE_ID, TABLE_ID, key, required=opts["required"])
        elif kind == "float":
            db.create_float_column(DATABASE_ID, TABLE_ID, key, required=opts["required"])
        elif kind == "boolean":
            db.create_boolean_column(DATABASE_ID, TABLE_ID, key, required=opts["required"])
        elif kind == "datetime":
            db.create_datetime_column(DATABASE_ID, TABLE_ID, key, required=opts["required"])
        elif kind == "enum":
            db.create_enum_column(
                DATABASE_ID, TABLE_ID, key, elements=opts["elements"], required=opts["required"]
            )
        else:  # pragma: no cover — spec is internal
            raise ValueError(f"unknown column type: {kind}")
        print(f"  column '{key}' ({kind}) created")


def _ensure_indexes(db: TablesDB) -> None:
    existing = {
        i.key
        for i in db.list_indexes(DATABASE_ID, TABLE_ID, queries=[Query.limit(100)]).indexes
    }
    for key, columns, orders, lengths in _INDEX_SPECS:
        if key in existing:
            continue
        db.create_index(
            DATABASE_ID,
            TABLE_ID,
            key,
            TablesDBIndexType.KEY,
            columns=columns,
            orders=orders,
            lengths=lengths or None,
        )
        print(f"  index '{key}' created")


def _smoke_test(db: TablesDB) -> None:
    """Create, read, and delete a throwaway row to prove writes work end-to-end."""
    now = datetime.now(timezone.utc).isoformat()
    row_id = f"smoke-test-{uuid.uuid4().hex[:8]}"
    data = {
        "account_id": "smoke-test-account",
        "child_name": "Smoke Test",
        "child_age_years": 6,
        "child_age_months": 72,
        "child_sex": "boy",
        "village": "Test",
        "consent_given": True,
        "consent_timestamp": now,
        "analysis_timestamp": now,
        "created_at": now,
        "updated_at": now,
        "estimated_height_cm": 115.2,
        "confirmed_weight_kg": 18.5,
        "bmi": 14.0,
        "who_percentile": 12.5,
        "who_category": "underweight",
        "who_chart_version": "who-2006-v1",
        "capture_quality": "good",
    }
    for symptom in SYMPTOMS:
        data[f"symptom_{symptom}_status"] = "not_assessed"
        data[f"symptom_{symptom}_confidence"] = 0.0
        data[f"symptom_{symptom}_model_ver"] = "v1.0"

    try:
        db.create_row(DATABASE_ID, TABLE_ID, row_id, data)
        db.get_row(DATABASE_ID, TABLE_ID, row_id)
        print(f"  smoke row '{row_id}' created + read back")
    finally:
        db.delete_row(DATABASE_ID, TABLE_ID, row_id)
        print(f"  smoke row '{row_id}' deleted")


def _verify(db: TablesDB) -> None:
    table = db.get_table(DATABASE_ID, TABLE_ID)
    # list_columns/indexes default to 25 results per page; the schema has more.
    columns = db.list_columns(
        DATABASE_ID, TABLE_ID, queries=[Query.limit(100)]
    ).columns
    indexes = db.list_indexes(
        DATABASE_ID, TABLE_ID, queries=[Query.limit(100)]
    ).indexes
    print(f"\n=== verification: table '{table.name}' ===")
    print(f"columns: {len(columns)} (expected {len(_COLUMN_SPECS)})")
    print(f"indexes: {len(indexes)} (expected {len(_INDEX_SPECS)})")
    if len(columns) != len(_COLUMN_SPECS) or len(indexes) != len(_INDEX_SPECS):
        sys.exit("verification failed: column/index count mismatch")


def main() -> None:
    db = TablesDB(_get_client())
    print(f"provisioning '{PROJECT_ID}' at {ENDPOINT}")
    _ensure_database(db)
    _ensure_table(db)
    _ensure_columns(db)
    _ensure_indexes(db)
    _smoke_test(db)
    _verify(db)
    print("\nsetup complete")


if __name__ == "__main__":
    main()
