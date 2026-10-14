# Manifest Converter

A Streamlit web app that converts PDF run manifests (delivery dockets) into clean Excel spreadsheets.

## ✨ Features

- Drag & drop PDF uploads in the browser
- Auto-detects route headers and merged cells
- Handles multi-page PDFs
- Export to `.xlsx` with auto-sized columns and frozen header row
- Combine multiple PDFs into a single workbook

## 🚀 Setup

**Prerequisite:** Python **3.10 – 3.13** (3.14+ may fail to build `pyarrow`)

```bash
# Clone the repo
git clone https://github.com/YOUR-USERNAME/manifest-converter.git
cd manifest-converter

# Create virtual environment
python -m venv .venv

# Activate (Windows)
.venv\Scripts\activate

# Activate (Mac/Linux)
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

## ▶️ Run

```bash
streamlit run app.py
```

Then open **http://localhost:8501** in your browser.

## 🧰 Requirements

- Python **3.10 – 3.13**
- See `requirements.txt` for Python packages

## 📂 Project Structure

```
manifest-converter/
├── app.py                 # Streamlit UI
├── convert_manifest.py    # PDF parsing logic
├── requirements.txt       # Python dependencies
├── .gitignore
└── README.md
```

## 🛠️ Troubleshooting

| Issue | Fix |
|---|---|
| `'streamlit' is not recognized` | Activate the venv first, or use `python -m streamlit run app.py` |
| `pyarrow` build error during install | Use Python 3.13, not 3.14+ |
| No data extracted from PDF | PDF is scanned (image, not text). Run OCR first with `ocrmypdf`. |

## 🔐 Data Privacy

This project **does not** store or transmit any uploaded files. All PDF processing happens locally in the Streamlit server running on your own machine.