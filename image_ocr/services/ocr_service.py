import pytesseract
from django.core.files.storage import default_storage
from PIL import Image


class OCRService:
    @staticmethod
    def extract_text_from_image(image_field):
        try:
            with open(image_field, "rb") as f:
                print(image_field)
                img = Image.open(f)
                print(img)
                return pytesseract.image_to_string(img)
        except Exception as e:
            raise ValueError(f"OCR processing failed: {str(e)}")
