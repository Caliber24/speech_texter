import os
from email.policy import default
import tempfile
import re
from rest_framework.viewsets import GenericViewSet, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from rest_framework.decorators import action
from .serializers import VTTSerializer
from .models import VTT
import uuid
from django.core.files.storage import default_storage
from .convertor import transcribe_audio
from django.core.files.uploadedfile import UploadedFile
from django.conf import settings
import os
from datetime import datetime
import logging

# Set up logging
logger = logging.getLogger(__name__)

# Create your views here.

class VTTViewSet(GenericViewSet, mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin,
                 mixins.DestroyModelMixin):
    serializer_class = VTTSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return VTT.objects.filter(user_id=self.request.user.id)
    
    def _get_unique_title(self, title, user):
        """
        Generate a unique title by appending a number in parentheses if the title already exists.
        
        Example:
        - Original: "My Title"
        - If exists: "My Title (1)"
        - If "My Title (1)" exists: "My Title (2)"
        
        If the title already has a number in parentheses, it will extract the base title
        and increment the counter from there.
        """
        # Check if the title already has a pattern like "Title (n)"
        base_title = title
        match = re.match(r'^(.*?)\s*\((\d+)\)$', title)
        if match:
            # Extract the base title and the current counter
            base_title = match.group(1).strip()
            
        counter = 0
        new_title = title
        
        # Check if the title already exists for this user
        while VTT.objects.filter(user=user, title=new_title).exists():
            counter += 1
            new_title = f"{base_title} ({counter})"
        
        return new_title

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        # Validate title is provided
        if not serializer.validated_data.get('title'):
            return Response(
                {"error": "Title is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Get a unique title
        original_title = serializer.validated_data.get('title')
        unique_title = self._get_unique_title(original_title, request.user)
        
        # Update the title if it was modified
        if original_title != unique_title:
            serializer.validated_data['title'] = unique_title
            
        audio_file: UploadedFile = serializer.validated_data.pop('audio')
        
        try:
            with tempfile.NamedTemporaryFile(suffix=os.path.splitext(audio_file.name)[1], delete=False) as tmp:
                for chunk in audio_file.chunks():
                    tmp.write(chunk)
                    tmp.flush()
                tmp.close()
                
                # Process the audio file
                transcription = transcribe_audio(tmp.name)
                
                # Save the VTT instance with user, title, and transcript
                vtt_instance = serializer.save(
                    user=request.user,
                    transcript=transcription
                )
                
                # Clean up the temporary file
                os.remove(tmp.name)
                
            return Response(self.get_serializer(vtt_instance).data, status=status.HTTP_201_CREATED)
        
        except Exception as e:
            logger.error(f"Error processing audio file: {str(e)}")
            return Response(
                {"error": f"Error processing audio file: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
    
    @action(detail=False, methods=['get'], url_path='after-timestamp')
    def get_posts_after_timestamp(self, request):
        """
        Get all posts created after the specified timestamp for the current user.
        
        Query Parameters:
        - timestamp: Unix timestamp (seconds since epoch)
        """
        timestamp_str = request.query_params.get('timestamp')
        
        if not timestamp_str:
            return Response(
                {"error": "timestamp parameter is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        try:
            # Convert Unix timestamp to datetime
            try:
                unix_timestamp = int(timestamp_str)
                timestamp = datetime.fromtimestamp(unix_timestamp)
            except ValueError:
                return Response(
                    {"error": "Invalid timestamp format. Use Unix timestamp (seconds since epoch)"},
                    status=status.HTTP_400_BAD_REQUEST
                )
                
            # Get posts after timestamp for the current user
            posts = VTT.objects.filter(
                user=request.user,
                created_at__gt=timestamp
            ).order_by('-created_at')
            
            # Serialize the results
            serializer = self.get_serializer(posts, many=True)
            
            return Response(
                {"posts": serializer.data},
                status=status.HTTP_200_OK
            )
            
        except Exception as e:
            logger.error(f"Error retrieving posts: {str(e)}")
            return Response(
                {"error": f"An error occurred: {str(e)}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )
