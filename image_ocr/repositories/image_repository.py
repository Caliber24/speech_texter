from image_ocr.models import ImageModel


class ImageRepository:
    @staticmethod
    def create_image(image_file, extracted_text=""):
        return ImageModel.objects.create(
            image=image_file, extracted_text=extracted_text
        )
