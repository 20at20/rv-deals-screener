"""
Tool: Google Sheets client
Layer: T (Tool) — stateless, input in / output out
"""

import os
import json
import gspread
from google.oauth2.service_account import Credentials

SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive.readonly",
]

_client: gspread.Client | None = None


def _get_client() -> gspread.Client:
    global _client
    if _client is not None:
        return _client

    credentials_path = os.environ.get("GOOGLE_CREDENTIALS_PATH")
    credentials_json = os.environ.get("GOOGLE_CREDENTIALS_JSON")

    if credentials_path:
        creds = Credentials.from_service_account_file(credentials_path, scopes=SCOPES)
    elif credentials_json:
        info = json.loads(credentials_json)
        creds = Credentials.from_service_account_info(info, scopes=SCOPES)
    else:
        raise EnvironmentError(
            "Set GOOGLE_CREDENTIALS_PATH or GOOGLE_CREDENTIALS_JSON in .env"
        )

    _client = gspread.authorize(creds)
    return _client


def get_pending_rows(sheet_id: str, sheet_name: str = "Sheet1") -> list[dict]:
    """Return all rows where 'Make analysis' == 'Yes'."""
    client = _get_client()
    sheet = client.open_by_key(sheet_id).worksheet(sheet_name)
    all_rows = sheet.get_all_records()
    pending = [row for row in all_rows if row.get("Make analysis") == "Yes"]
    print(f"[sheets] Found {len(pending)} pending rows in '{sheet_name}'")
    return pending


def get_feedback_rows(sheet_id: str, sheet_name: str = "Sheet1") -> list[dict]:
    """Return rows where 'Analyst Note' is non-empty and 'Analyst Implemented' != 'Yes'."""
    client = _get_client()
    sheet = client.open_by_key(sheet_id).worksheet(sheet_name)
    all_rows = sheet.get_all_records()
    feedback = [
        row for row in all_rows
        if row.get("Analyst Note", "").strip()
        and row.get("Analyst Implemented", "").strip() != "Yes"
    ]
    print(f"[sheets] Found {len(feedback)} unprocessed feedback rows in '{sheet_name}'")
    return feedback


def update_row(
    sheet_id: str,
    sheet_name: str,
    match_col: str,
    match_val: str,
    updates: dict,
) -> None:
    """
    Find the row where match_col == match_val and update the given columns.
    Fails loudly if the row is not found.
    """
    client = _get_client()
    worksheet = client.open_by_key(sheet_id).worksheet(sheet_name)

    headers = worksheet.row_values(1)
    all_values = worksheet.get_all_values()

    if match_col not in headers:
        raise ValueError(f"[sheets] Column '{match_col}' not found in sheet headers")

    match_col_idx = headers.index(match_col)
    row_index = None

    for i, row in enumerate(all_values[1:], start=2):  # skip header, 1-indexed
        if len(row) > match_col_idx and row[match_col_idx].strip() == match_val:
            row_index = i
            break

    if row_index is None:
        raise LookupError(
            f"[sheets] Row with {match_col}='{match_val}' not found — cannot update"
        )

    for col_name, value in updates.items():
        if col_name not in headers:
            print(f"[sheets] WARNING: column '{col_name}' not in sheet, skipping")
            continue
        col_idx = headers.index(col_name) + 1  # gspread is 1-indexed
        worksheet.update_cell(row_index, col_idx, str(value) if value is not None else "")

    print(f"[sheets] Updated row {row_index} ({match_col}='{match_val}')")
