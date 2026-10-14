"""
app.py
------
Streamlit web app: upload run manifest PDFs → download as Excel.
"""

import io
import datetime as dt

import pandas as pd
import streamlit as st

from convert_manifest import pdf_to_dataframe


# ---------- Page setup ----------
st.set_page_config(
    page_title="Run Manifest → Excel",
    page_icon="📦",
    layout="wide",
)

st.title("📦 Run Manifest → Excel Converter")
st.caption(
    "Upload one or more PDF run manifests. Preview the extracted rows "
    "and download everything as a single Excel workbook."
)

# ---------- Sidebar options ----------
with st.sidebar:
    st.header("Options")
    combine_files = st.checkbox(
        "Combine all uploads into one sheet",
        value=True,
        help="If off, each PDF gets its own sheet in the Excel file.",
    )
    show_raw = st.checkbox("Show raw table (for debugging)", value=False)
    st.divider()
    st.markdown(
        "**Tips**\n"
        "- PDFs must contain *text* tables, not scans.\n"
        "- If you see *'No table data found'*, the PDF is likely an image."
    )

# ---------- File uploader ----------
uploads = st.file_uploader(
    "Choose PDF file(s)",
    type=["pdf"],
    accept_multiple_files=True,
)

# ---------- Main logic ----------
if not uploads:
    st.info("👆 Upload a PDF to get started.")
    st.stop()

# Parse every uploaded file
parsed = []          # list of (filename, dataframe)

for uploaded_file in uploads:
    st.subheader(f"📄 {uploaded_file.name}")

    try:
        df = pdf_to_dataframe(uploaded_file)
    except Exception as exc:
        st.error(f"Failed to parse **{uploaded_file.name}**: {exc}")
        continue

    if df.empty:
        st.warning("No table data was found in this PDF.")
        continue

    df.insert(0, "Source File", uploaded_file.name)
    parsed.append((uploaded_file.name, df))

    st.success(f"Extracted **{len(df)} rows** and **{len(df.columns)} columns**.")

    with st.expander("Preview extracted data", expanded=True):
        st.dataframe(df, use_container_width=True, height=350)

    if show_raw:
        with st.expander("Raw string view"):
            st.text(df.to_string())

# ---------- Build Excel & download ----------
if parsed:
    st.divider()
    st.subheader("Download")

    buffer = io.BytesIO()

    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        if combine_files:
            combined = pd.concat([df for _, df in parsed], ignore_index=True)
            combined.to_excel(writer, index=False, sheet_name="Manifest")

            # Auto-size columns on the combined sheet
            ws = writer.sheets["Manifest"]
            for col_idx, col_name in enumerate(combined.columns, start=1):
                max_len = max(
                    combined[col_name].astype(str).map(len).max() if len(combined) else 0,
                    len(str(col_name)),
                )
                col_letter = ws.cell(row=1, column=col_idx).column_letter
                ws.column_dimensions[col_letter].width = min(max_len + 2, 60)
            ws.freeze_panes = "A2"

        else:
            for filename, df in parsed:
                # Excel sheet names: max 31 chars, no []:*?/\
                sheet_name = (
                    filename.replace(".pdf", "")
                    .translate(str.maketrans("", "", "[]:*?/\\"))
                )[:31] or "Sheet"
                df.to_excel(writer, index=False, sheet_name=sheet_name)

                ws = writer.sheets[sheet_name]
                for col_idx, col_name in enumerate(df.columns, start=1):
                    max_len = max(
                        df[col_name].astype(str).map(len).max() if len(df) else 0,
                        len(str(col_name)),
                    )
                    col_letter = ws.cell(row=1, column=col_idx).column_letter
                    ws.column_dimensions[col_letter].width = min(max_len + 2, 60)
                ws.freeze_panes = "A2"

    buffer.seek(0)

    timestamp = dt.datetime.now().strftime("%Y%m%d_%H%M%S")
    st.download_button(
        label="⬇️  Download Excel (.xlsx)",
        data=buffer,
        file_name=f"run_manifest_{timestamp}.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
        type="primary",
    )

    # Summary of what's about to be downloaded
    total_rows = sum(len(df) for _, df in parsed)
    st.caption(f"Ready to download **{len(parsed)} file(s)** — **{total_rows} total rows**.")
else:
    st.error("No usable data was extracted from any uploaded file.")