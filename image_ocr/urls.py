from image_ocr.views import ImageOCRView, PDFOCRView
from django.urls import path


urlpatterns = [
    path("ocr-image/", ImageOCRView.as_view(), name="ocr-process"),
    path("ocr-pdf/", PDFOCRView.as_view(), name="ocr-pdf"),
]
