import os
import shutil
import subprocess
import pandas as pd
from datetime import datetime

UNPROCESSED_DIR = "unprocessed"
PROCESSED_DIR = "processed"
LOG_FILE = "batch_log.txt"
COMBINED_CSV = "all_transactions_combined.csv"

# Ensure folders exist
os.makedirs(UNPROCESSED_DIR, exist_ok=True)
os.makedirs(PROCESSED_DIR, exist_ok=True)

# Start a fresh log
with open(LOG_FILE, "w", encoding="utf-8") as log:
    log.write(f"Batch run started: {datetime.now()}\n\n")

# Gather PDFs
pdf_files = [f for f in os.listdir(UNPROCESSED_DIR) if f.lower().endswith(".pdf")]
combined_dataframes = []

if not pdf_files:
    print("📂 No PDF files found in 'unprocessed'. Nothing to process.")
    with open(LOG_FILE, "a", encoding="utf-8") as log:
        log.write("No PDF files found.\n")
else:
    for filename in pdf_files:
        input_path = os.path.join(UNPROCESSED_DIR, filename)
        base_name = os.path.splitext(filename)[0]
        output_csv = f"extracted_{base_name}.csv"

        print(f"\n🚀 Processing: {filename}")
        with open(LOG_FILE, "a", encoding="utf-8") as log:
            log.write(f"--- Processing {filename} ---\n")

        result = subprocess.run(
            ["python", "-X", "utf8", "extract_transactions.py", input_path],
            capture_output=True,
            text=True,
            encoding="utf-8",
            errors="replace"  # this will replace any weird bytes with �
        )

        # Log stdout and stderr
        with open(LOG_FILE, "a", encoding="utf-8") as log:
            if result.stdout:
                log.write(result.stdout)
            if result.stderr:
                log.write("\n[stderr]\n" + result.stderr)
            log.write("\n")


        # Rename and store CSV
        if os.path.exists("extracted_transactions.csv"):
            os.rename("extracted_transactions.csv", output_csv)
            print(f"✅ Saved: {output_csv}")

            # Add to combined DataFrame
            df = pd.read_csv(output_csv)
            df["source_file"] = base_name  # track origin
            combined_dataframes.append(df)

        # Move processed PDF
        shutil.move(input_path, os.path.join(PROCESSED_DIR, filename))
        print(f"📁 Moved {filename} to 'processed/'")

    # Save combined CSV
    if combined_dataframes:
        combined = pd.concat(combined_dataframes, ignore_index=True)
        combined.to_csv(COMBINED_CSV, index=False)
        print(f"\n📦 Combined CSV saved as '{COMBINED_CSV}'")
        with open(LOG_FILE, "a", encoding="utf-8") as log:
            log.write(f"\nCombined file saved: {COMBINED_CSV}\n")

    print("\n🎉 Batch complete.")
