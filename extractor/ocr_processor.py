import fitz  # PyMuPDF
from PIL import Image
import pytesseract
import os
import gc
from extractor.config import TESSERACT_CMD

pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD


def ocr_image_page(pdf_path, page_number):
    try:
        doc = fitz.open(pdf_path)
        page = doc.load_page(page_number)
        pix = page.get_pixmap(dpi=300)
        temp_dir = "temp"

        os.makedirs(temp_dir, exist_ok=True)
        img_path = os.path.join(temp_dir, f"page_{page_number + 1}.png")
        pix.save(img_path)
        image = Image.open(img_path)

        ocr_data = pytesseract.image_to_data(image, output_type=pytesseract.Output.DATAFRAME)
        ocr_data = ocr_data.dropna(subset=['text'])
        ocr_data = ocr_data[ocr_data['text'].str.strip() != '']

        if ocr_data.empty:
            print(f"OCR data is empty for page {page_number + 1}")
            return ""

        grouped = ocr_data.groupby(['block_num', 'par_num', 'line_num'])

        lines = []
        for _, group in grouped:
            sorted_words = group.sort_values('left')
            line_text = " ".join(sorted_words['text'].tolist())
            lines.append(line_text)

        result_text = "\n".join(lines)

        print(f"OCR successfully completed page {page_number + 1}")
        return result_text

    except Exception as e:
        print(f"OCR failed on page {page_number + 1}: {e}")
        return ""

    finally:
        gc.collect()
