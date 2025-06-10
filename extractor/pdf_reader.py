import pdfplumber

def extract_table_pdfplumber(pdf_path, page_number):
    try:
        with pdfplumber.open(pdf_path) as pdf:
            if page_number < len(pdf.pages):
                page = pdf.pages[page_number]
                tables = page.extract_tables()
                if tables:
                    print(f"Table found on page {page_number + 1}")
                    return tables[0]
    except Exception as e:
        print(f"Error extracting table page {page_number + 1}: {e}")
    return []
