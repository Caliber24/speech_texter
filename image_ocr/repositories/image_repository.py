from image_ocr.models import ImageModel
from django.utils import timezone
from django.db.models import Q


class ImageRepository:
    @staticmethod
    def create_image(image_file, extracted_text="", title=None, user_id=None):
        return ImageModel.objects.create(
            image=image_file, 
            extracted_text=extracted_text,
            title=title,
            user_id=user_id
        )
        
    @staticmethod
    def get_user_posts_after_timestamp(user_id, timestamp):
        """
        Retrieve all posts for a user created after the given timestamp
        """
        return ImageModel.objects.filter(
            user_id=user_id,
            created_at__gt=timestamp
        ).order_by('-created_at')
    
    @staticmethod
    def get_unique_title(title, user_id=None):
        """
        Generate a unique title by adding an incremented number in parentheses
        if the title already exists for the user
        
        Example:
        - Original: "My Title"
        - If exists: "My Title (1)"
        - If "My Title (1)" exists: "My Title (2)"
        """
        # Base query to check for duplicate titles
        query = Q(title=title)
        
        # If we have a user_id, only check for duplicates for that user
        if user_id:
            query &= Q(user_id=user_id)
            
        # Check if the exact title exists
        if ImageModel.objects.filter(query).exists():
            # Title exists, so we need to find the next available number
            counter = 1
            while True:
                new_title = f"{title} ({counter})"
                query_with_counter = Q(title=new_title)
                if user_id:
                    query_with_counter &= Q(user_id=user_id)
                    
                if not ImageModel.objects.filter(query_with_counter).exists():
                    return new_title
                counter += 1
        
        # Title doesn't exist, return as is
        return title
