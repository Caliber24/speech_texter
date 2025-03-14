from rest_framework import serializers
from django.core.validators import FileExtensionValidator
from ..models import ImageModel
from django.conf import settings


class ImageUploadSerializer(serializers.ModelSerializer):
    title = serializers.CharField(max_length=255, required=True)
    user_id = serializers.CharField(max_length=255, required=True)
    
    class Meta:
        model = ImageModel
        fields = ["image", "title", "user_id"]
        extra_kwargs = {
            "image": {
                "required": True,
                "allow_empty_file": False,
                "use_url": True,
                "max_length": settings.UPLOAD_IMAGE_SIZE_LIMIT_MB * 1024 * 1024,
            }
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # افزودن اعتبارسنج پسوند فایل
        self.fields["image"].validators.append(
            FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png"])
        )

    def validate_image(self, value):
        # اعتبارسنجی نوع MIME واقعی
        valid_mime_types = ["image/jpeg", "image/png", "image/jpg"]
        if value.content_type not in valid_mime_types:
            raise serializers.ValidationError("نوع فایل تصویر معتبر نیست")

        # اعتبارسنجی سایز فایل
        if value.size > settings.UPLOAD_IMAGE_SIZE_LIMIT_MB * 1024 * 1024:
            raise serializers.ValidationError(
                f"حجم فایل نباید بیشتر از {settings.UPLOAD_IMAGE_SIZE_LIMIT_MB} مگابایت باشد"
            )

        return value

    def validate_user_id(self, value):
        if not value or value.strip() == "":
            raise serializers.ValidationError("شناسه کاربر نمی‌تواند خالی باشد")
        return value
        
    def validate_title(self, value):
        if not value or value.strip() == "":
            raise serializers.ValidationError("عنوان نمی‌تواند خالی باشد")
        return value
