from pdf2image import convert_from_path
import tempfile
import os
from django.conf import settings
import fitz


class PDFService:
    @staticmethod
    def convert_pdf_to_images(pdf_path, zoom=3):
        """تبدیل PDF به تصویر با PyMuPDF"""
        try:
            doc = fitz.open(pdf_path)
            image_paths = []

            for page_num in range(len(doc)):
                page = doc.load_page(page_num)
                mat = fitz.Matrix(zoom, zoom)
                pix = page.get_pixmap(matrix=mat)
                img_path = f"page_{page_num+1}.png"
                pix.save(img_path)
                image_paths.append(img_path)

            return image_paths
        except Exception as e:
            raise ValueError(f"PDF conversion failed: {str(e)}")
