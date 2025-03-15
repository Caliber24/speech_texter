from django.db import models


class ImageModel(models.Model):
    image = models.ImageField(upload_to="ocr_images/")
    extracted_text = models.TextField(blank=True)
    title = models.CharField(max_length=255, blank=True, null=True)
    user_id = models.CharField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.title or f'Image {self.id}'}"
