import streamlit as st
import os
import csv
import requests
import shutil
from zipfile import ZipFile

st.set_page_config(page_title="Regulations.gov Comment Scraper", layout="centered")

st.title("Regulations.gov Comment PDF Downloader")

# Step 1: Instructions to Request CSV
st.header("Step 1: Request Bulk CSV")
st.markdown("""
Go to [**Regulations.gov Bulk Download Page**](https://www.regulations.gov/bulkdownload) and request the comment data for your docket.

1. Enter the **Docket ID** (e.g., `CMS-2025-0050`). This can be found at the top of the Docket Details page on the comment docket you are on.
2. Enter your **email address**
3. Submit the form — you will receive a CSV by email

Once you have the file, upload it below.
""")

st.divider()

# Step 2: Upload CSV
st.header("Step 2: Upload Bulk CSV from Email")
uploaded_csv = st.file_uploader("Upload the CSV file sent to your email", type=["csv"])

if uploaded_csv:
    csv_filename = uploaded_csv.name
    with open(csv_filename, "wb") as f:
        f.write(uploaded_csv.getbuffer())

    docket = csv_filename.split('.')[0]
    output_dir = f"{docket}_comments"
    os.makedirs(output_dir, exist_ok=True)

    st.info("Processing CSV and downloading first PDFs...")

    with open(csv_filename, newline='', encoding='utf-8') as csvfile:
        reader = csv.DictReader(csvfile)
        success = 0
        skipped = 0
        for i, row in enumerate(reader, start=1):
            attachments = row.get("Attachment Files", "")
            if not attachments or ".pdf" not in attachments.lower():
                skipped += 1
                continue

            pdf_links = [url.strip() for url in attachments.split(",") if url.strip().lower().endswith(".pdf")]
            if not pdf_links:
                skipped += 1
                continue

            first_pdf = pdf_links[0]
            org = row.get("Organization", "").strip()
            tracking = row.get("Tracking Number", "").strip()
            base_name = f"{org if org else tracking} Comment.pdf"
            filename = "".join(c for c in base_name if c.isalnum() or c in " ._-").strip()
            filepath = os.path.join(output_dir, filename)

            try:
                pdf = requests.get(first_pdf, timeout=10)
                pdf.raise_for_status()
                with open(filepath, "wb") as f:
                    f.write(pdf.content)
                success += 1
            except Exception:
                skipped += 1

        shutil.copy(csv_filename, os.path.join(output_dir, csv_filename))
        zip_filename = f"{docket}_comments.zip"
        shutil.make_archive(zip_filename.replace(".zip", ""), 'zip', output_dir)

        st.success(f"Download complete: {success} PDFs saved, {skipped} skipped.")
        with open(zip_filename, "rb") as f:
            st.download_button("Download ZIP of PDFs", f, file_name=zip_filename)