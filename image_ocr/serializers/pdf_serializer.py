from rest_framework import serializers
from django.conf import settings
from django.core.validators import FileExtensionValidator
from PyPDF2 import PdfReader


class PDFUploadSerializer(serializers.Serializer):
    pdf = serializers.FileField(
        required=True,
        allow_empty_file=False,
        max_length=settings.PDF_SIZE_LIMIT_MB * 1024 * 1024,  # 20MB
        validators=[
            FileExtensionValidator(allowed_extensions=["pdf"]),  # اعتبارسنجی پسوند فایل
        ],
    )
    title = serializers.CharField(max_length=255, required=True)
    user_id = serializers.CharField(max_length=255, required=True)

    def validate_pdf(self, value):
        # اعتبارسنجی نوع MIME واقعی فایل
        if value.content_type != "application/pdf":
            raise serializers.ValidationError("فایل ارسالی باید از نوع PDF باشد")

        # اعتبارسنجی تعداد صفحات
        try:

            value.seek(0)  # برگشت به ابتدای فایل
            pdf = PdfReader(value)
            if len(pdf.pages) > settings.PDF_PAGE_LIMIT:
                raise serializers.ValidationError(
                    f"تعداد صفحات نباید بیشتر از {settings.PDF_PAGE_LIMIT} باشد"
                )
        except Exception as e:
            if isinstance(e, serializers.ValidationError):
                raise e
            raise serializers.ValidationError(f"خطا در خواندن PDF: {str(e)}")

        return value
        
    def validate_user_id(self, value):
        if not value or value.strip() == "":
            raise serializers.ValidationError("شناسه کاربر نمی‌تواند خالی باشد")
        return value
        
    def validate_title(self, value):
        if not value or value.strip() == "":
            raise serializers.ValidationError("عنوان نمی‌تواند خالی باشد")
        return value
