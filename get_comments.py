import os
import csv
import requests

INPUT_CSV = "CMS-2025-0050.csv"  # Replace with your filename
OUTPUT_DIR = "CMS-2025-0050 comments"

os.makedirs(OUTPUT_DIR, exist_ok=True)

with open(INPUT_CSV, newline='', encoding='utf-8') as csvfile:
    reader = csv.DictReader(csvfile)
    for row in reader:
        attachment_field = row["Attachment Files"]
        if not attachment_field or ".pdf" not in attachment_field.lower():
            continue

        pdf_links = [url.strip() for url in attachment_field.split(",") if url.strip().lower().endswith(".pdf")]
        if not pdf_links:
            continue

        first_pdf = pdf_links[0]
        org = row["Organization Name"].strip() if row["Organization Name"].strip() else None
        tracking = row["Tracking Number"].strip()
        base_name = f"{org or tracking} Comment.pdf"

        # Clean filename
        filename = "".join(c for c in base_name if c.isalnum() or c in " ._-").strip()
        filepath = os.path.join(OUTPUT_DIR, filename)

        try:
            r = requests.get(first_pdf, timeout=10)
            r.raise_for_status()
            with open(filepath, "wb") as f:
                f.write(r.content)
            print(f"Downloaded: {filename}")
        except Exception as e:
            print(f"Failed to download {first_pdf}: {e}")

# Save the CSV in the folder too
import shutil
shutil.copy(INPUT_CSV, os.path.join(OUTPUT_DIR, os.path.basename(INPUT_CSV)))