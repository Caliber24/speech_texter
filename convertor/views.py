import os
from email.policy import default
import tempfile
from rest_framework.viewsets import GenericViewSet, mixins
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import VTTSerializer
from .models import VTT
import uuid
from django.core.files.storage import default_storage
from .convertor import transcribe_audio
from django.core.files.uploadedfile import UploadedFile
from django.conf import settings
import os


# Create your views here.

class VTTViewSet(GenericViewSet, mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin,
                 mixins.DestroyModelMixin):
    serializer_class = VTTSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return VTT.objects.filter(user_id=self.request.user.id)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        audio_file: UploadedFile = serializer.validated_data['audio']
        print(audio_file)
        
        with tempfile.NamedTemporaryFile(suffix=os.path.splitext(audio_file.name)[1], delete=False) as tmp:
            for chunk in audio_file.chunks():
                tmp.write(chunk)
                tmp.flush()
            tmp.close()
            transcription = transcribe_audio(tmp.name)     
            vtt_instance = serializer.save(user=request.user, audio=audio_file.name, transcript=transcription)
            os.remove(tmp.name)
        return Response(VTTSerializer(vtt_instance).data, status=status.HTTP_201_CREATED)
