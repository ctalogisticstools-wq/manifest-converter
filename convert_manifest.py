"""
convert_manifest.py
-------------------
Parses run manifest PDFs into a pandas DataFrame.

Handles:
  * Merged "Customer/Destination" cells (route headers like ALTONA(79))
  * Multi-page PDFs
  * <br> tags inside delivery instructions
  * Repeated header rows on each page
"""

import io
import re
from pathlib import Path

import pdfplumber
import pandas as pd


# Exact column order as they appear in the PDF
COLUMNS = [
    "Customer/Destination",
    "Window FROM",
    "Window TO",
    "Inv. #",
    "COD",
    "Cust.",
    "Delivery Instructions",
    "Docket Notes",
    "Run Comments",
]


def clean_cell(value) -> str:
    """Normalize a single cell value from pdfplumber."""
    if value is None:
        return ""
    text = str(value).replace("<br>", "\n")   # real line breaks
    text = re.sub(r"[ \t]+", " ", text)        # collapse runs of spaces/tabs
    text = re.sub(r"\n{2,}", "\n", text)       # collapse blank lines
    return text.strip()


def is_route_header(text: str) -> bool:
    """
    Detect a route header row like 'ALTONA(79)' or 'SADIE(83)'.
    Pattern: NAME(<digits>)  — name may contain letters, spaces, @, &, -, ., '
    """
    if not text:
        return False
    return bool(re.match(r"^[A-Z0-9@&'\-\. ]+\(\d+\)\s*$", text.strip(), re.IGNORECASE))


def extract_rows_from_table(table) -> list[dict]:
    """Turn one pdfplumber table (list of lists) into clean row dicts."""
    rows = []
    current_route = ""

    for raw_row in table:
        # Normalise row length to match COLUMNS
        row = list(raw_row) + [""] * (len(COLUMNS) - len(raw_row))
        row = row[: len(COLUMNS)]

        first_cell = clean_cell(row[0])

        # --- Case 1: Route header row (e.g., "ALTONA(79)") ---
        # Route headers only have text in the first cell.
        if is_route_header(first_cell) and not any(clean_cell(c) for c in row[1:]):
            current_route = first_cell
            continue

        # --- Case 2: The PDF's own header row → skip ---
        if first_cell.lower().startswith("customer/destination"):
            continue

        # --- Case 3: Completely empty row → skip ---
        if not any(clean_cell(c) for c in row):
            continue

        # --- Case 4: Real data row ---
        record = {col: clean_cell(row[i]) for i, col in enumerate(COLUMNS)}

        # If customer cell is empty, the route name bled through — fill it down
        if not record["Customer/Destination"]:
            record["Customer/Destination"] = current_route

        record["Route"] = current_route
        rows.append(record)

    return rows


def pdf_to_dataframe(source) -> pd.DataFrame:
    """
    Extract all tables from a PDF and return a DataFrame.

    `source` may be:
      - a file path (str or Path)
      - a file-like object (e.g. Streamlit UploadedFile, io.BytesIO)
    """
    # If it's a Streamlit upload, get its bytes so we can re-open per page.
    if hasattr(source, "read"):
        source.seek(0)
        pdf_bytes = source.read()
        pdf_source = io.BytesIO(pdf_bytes)
    else:
        pdf_source = str(source)

    all_rows = []

    with pdfplumber.open(pdf_source) as pdf:
        for page_num, page in enumerate(pdf.pages, start=1):
            tables = page.extract_tables()
            for table in tables:
                rows = extract_rows_from_table(table)
                for r in rows:
                    r["Source Page"] = page_num
                all_rows.extend(rows)

    df = pd.DataFrame(all_rows)

    # Put Route first, then PDF columns, then Source Page
    if not df.empty:
        ordered = ["Route"] + COLUMNS + ["Source Page"]
        ordered = [c for c in ordered if c in df.columns]
        df = df[ordered]

    return df