import pandas as pd
import json
import os
import argparse
from extractor.config import PDF_PATH, OUTPUT_EXCEL
from extractor.pdf_reader import extract_table_pdfplumber
from extractor.ocr_processor import ocr_image_page
from extractor.excel_writer import save_to_excel


def valid_table(table_data, expected_headers):
    if not table_data or len(table_data) < 2:
        return False

    header_row = table_data[0]
    matched = sum(1 for col in expected_headers if col in header_row)
    return matched / len(expected_headers) >= 0.6


def assign_columns(page_df, column_expectations, page_number):
    try:
        actual_cols = page_df.shape[1]
        expected_cols = len(column_expectations)

        if actual_cols == expected_cols:
            page_df.columns = column_expectations
        elif actual_cols < expected_cols:
            page_df.columns = column_expectations[:actual_cols]
            print(f"Warning: Page {page_number + 1} has fewer columns. Assigned partial headers.")
        else:
            page_df = page_df.iloc[:, :expected_cols]
            page_df.columns = column_expectations
            print(f"Warning: Page {page_number + 1} has extra columns. Extra columns discarded.")
    except Exception as e:
        print(f"Could not assign columns due to mismatch on page {page_number + 1}: {e}")
        page_df.columns = [f"Col_{i+1}" for i in range(page_df.shape[1])]
    return page_df


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('--extraction_config', required=True)
    args = parser.parse_args()

    try:
        if os.path.isfile(args.extraction_config):
            with open(args.extraction_config, 'r') as file:
                config_data = json.load(file)
        else:
            config_data = json.loads(args.extraction_config)
        config_data = {int(k): v for k, v in config_data.items()}
    except Exception as err:
        print("Failed to parse extraction config: Invalid JSON?", err)
        return

    extracted_tables = {}

    for pg_num, column_expectations in config_data.items():
        page_df = pd.DataFrame()
        table_raw = extract_table_pdfplumber(PDF_PATH, pg_num)

        if valid_table(table_raw, column_expectations):
            print(f"Found decent table on page {pg_num + 1}.")
            try:
                page_df = pd.DataFrame(table_raw[1:], columns=table_raw[0])
                page_df = page_df.loc[:, page_df.columns.isin(column_expectations)]
                page_df = assign_columns(page_df, column_expectations, pg_num)
                extracted_tables[pg_num + 1] = page_df
                continue
            except Exception as e:
                print(f"Problem while building DataFrame from PDF table: {e}")

        print(f"Falling back to OCR on page {pg_num + 1}...")
        text_blob = ocr_image_page(PDF_PATH, pg_num)
        text_lines = [line.strip() for line in text_blob.splitlines() if len(line.strip()) > 10]
        rows = [line.split() for line in text_lines]

        if rows:
            try:
                page_df = pd.DataFrame(rows)
                page_df = assign_columns(page_df, column_expectations, pg_num)
                if not page_df.empty:
                    extracted_tables[pg_num + 1] = page_df
            except Exception as e:
                print(f"Could not construct DataFrame from OCR text on page {pg_num + 1}: {e}")
        else:
            print(f"No usable data extracted from page {pg_num + 1}")

    if extracted_tables:
        save_to_excel(extracted_tables, OUTPUT_EXCEL)
        print(f"\n Done! Results written to: {OUTPUT_EXCEL}")
    else:
        print("\n Extraction produced no usable results. Please check input.")


if __name__ == "__main__":
    main()
