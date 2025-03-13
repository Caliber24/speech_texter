from rest_framework import serializers
from django.core.validators import FileExtensionValidator
from ..models import ImageModel
from django.conf import settings


class ImageUploadSerializer(serializers.ModelSerializer):
    class Meta:
        model = ImageModel
        fields = ["image"]
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
