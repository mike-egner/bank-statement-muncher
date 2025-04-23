## 📘 `README.md`

Create a file named `README.md` in your project root with the following:


# Bank Statement Processing Tool

This is a Python-based command-line and GUI tool for parsing PDF bank statements, categorizing transactions, and exporting clean CSVs for accounting and tax purposes.

## Features

- ✅ Extracts transactions from PDF bank statements
- ✅ Automatically categorizes transactions using keyword rules
- ✅ Logs and validates opening/closing balance reconciliation
- ✅ Batch processes multiple PDFs from an `unprocessed/` folder
- ✅ Outputs per-file CSVs and one combined CSV
- ✅ GUI version available for viewing and editing
- ✅ Rules easily customized via `categories_rules.py`

## Getting Started

### 1. Install Requirements

```bash
pip install -r requirements.txt
```

### 2. Prepare Folders

Create two folders in your project root:

```
unprocessed/
processed/
```

Place PDF statements in `unprocessed/`.

### 3. Run Batch Processor

```bash
python batch_extract_transactions.py
```

This will:
- Extract and categorize transactions
- Move PDFs to `processed/`
- Save CSVs and logs in the root directory

### 4. Optional: Run GUI App

```bash
python gui_tk_table.py
```

Use the GUI to preview, edit, and save categorized CSVs.

## Customize Categorization

Edit `categories_rules.py` to define keyword-based transaction rules.

```python
rules = {
    "uber": "Transport",
    "google": "Software",
    "woolworths": "Groceries",
    # Add your own...
}
```

## Outputs

- `extracted_<filename>.csv` – One per PDF
- `all_transactions_combined.csv` – Combined output
- `batch_log.txt` – Full log of extraction and errors
