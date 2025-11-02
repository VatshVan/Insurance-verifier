import pytesseract
from PIL import Image
import logging

def perform_ocr(pil_image):
    """
    Performs OCR on a PIL Image object and returns the extracted text.
    The 'pil_image' argument is expected to be a PIL Image object,
    not a file path or file-like object.
    """
    try:
        text = pytesseract.image_to_string(pil_image, lang='eng')
        
        if not text.strip():
            logging.warning("OCR returned no text. Check image quality.")
            return "OCR processing complete, but no text was detected."
            
        return text
        
    except pytesseract.TesseractNotFoundError:
        logging.error("Tesseract executable not found. Make sure it's installed and in your system's PATH.")
        return "ERROR: Tesseract OCR engine not found. Please ensure it's installed and added to your system PATH."
    except Exception as e:
        logging.error(f"An error occurred during OCR processing: {e}")
        return f"An error occurred: {e}"