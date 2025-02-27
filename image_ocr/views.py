from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .serializers.image_serializer import ImageUploadSerializer
from .services.ocr_service import OCRService
from .repositories.image_repository import ImageRepository
import os
from .services.pdf_service import PDFService
from .serializers.pdf_serializer import PDFUploadSerializer
from tempfile import NamedTemporaryFile


class ImageOCRView(APIView):
    """
    POST:
    دریافت عکس و برگرداندن متن استخراج شده
    """

    def post(self, request):
        serializer = ImageUploadSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            image_file = serializer.validated_data["image"]

            # Save image
            image_instance = ImageRepository.create_image(image_file)
            # Process OCR
            extracted_text = OCRService.extract_text_from_image(
                image_instance.image.path
            )

            # Update instance
            image_instance.extracted_text = extracted_text
            image_instance.save()

            return Response(
                {
                    "id": image_instance.id,
                    "text": extracted_text,
                    "image_url": image_instance.image.url,
                },
                status=status.HTTP_201_CREATED,
            )

        except Exception as e:
            import sys

            return Response(
                {"error": str(e) + "-" + str(type(e)) + str(sys.exc_info())},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


class PDFOCRView(APIView):
    """
    POST:
    دریافت PDF و برگرداندن متن استخراج شده با شماره صفحات
    """

    def post(self, request):
        serializer = PDFUploadSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(
                {"error": serializer.errors}, status=status.HTTP_400_BAD_REQUEST
            )

        try:
            pdf_file = serializer.validated_data["pdf"]

            # ذخیره موقت PDF
            with NamedTemporaryFile(delete=False, suffix=".pdf") as tmp_pdf:
                for chunk in pdf_file.chunks():
                    tmp_pdf.write(chunk)
                pdf_path = tmp_pdf.name

            # تبدیل به عکس
            image_paths = PDFService.convert_pdf_to_images(pdf_path)

            # پردازش OCR
            results = []
            for page_num, image_path in enumerate(image_paths, start=1):
                text = OCRService.extract_text_from_image(image_path)
                results.append({"page": page_num, "text": text.strip()})
                # حذف فایل عکس
                os.remove(image_path)

            # حذف فایل PDF موقت
            os.remove(pdf_path)

            return Response({"pages": results}, status=status.HTTP_200_OK)

        except Exception as e:
            # حذف فایلهای باقیمانده در صورت خطا
            if "pdf_path" in locals() and os.path.exists(pdf_path):
                os.remove(pdf_path)
            if "image_paths" in locals():
                for path in image_paths:
                    if os.path.exists(path):
                        os.remove(path)
            return Response(
                {"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
