from django.db import models


class ImageModel(models.Model):
    image = models.ImageField(upload_to="ocr_images/")
    extracted_text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Image {self.id}"
