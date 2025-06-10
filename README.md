# PDF Table & OCR Extraction

## Setup Instructions

1. **Install Tesseract OCR**

   Download and install Tesseract from:  
   https://github.com/tesseract-ocr/tesseract/wiki

   Install it in this path:  
   `C:\Program Files\Tesseract-OCR\tesseract.exe`

2. **Create virtual environment**
   python -m venv env

3. **Activate the virtual environment**
    ./env/Scripts/activate

4. **Install required packages**
    pip install -r requirements.txt

5. **Run the extraction script**
    python main.py --extraction_config extraction_config.json

Notes: Place the source file under the data folder.