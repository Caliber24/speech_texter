import os.path
import whisper
from rest_framework.viewsets import ModelViewSet, GenericViewSet, mixins, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import VTTSerializer
from .models import VTT

import os
# Create your views here.


class VTTViewSet(GenericViewSet, mixins.CreateModelMixin, mixins.ListModelMixin, mixins.RetrieveModelMixin, mixins.DestroyModelMixin):
  serializer_class = VTTSerializer
  permission_classes = [IsAuthenticated]
  def get_queryset(self):
      return VTT.objects.filter(user_id=self.request.user.id)
  
  def perform_create(self, serializer):
    instance = serializer.save(user=self.request.user)
    audio_file_path = os.path.abspath(instance.audio_path)
    print(audio_file_path)
    try:
      transcript = self.convert_audio_to_text(audio_file_path)
      instance.transcript = transcript
      instance.save()
    except Exception as e:
      print(f"Error during audio-to-text conversion: {e}" )
      return Response({'error': e},  status=status.HTTP_500_INTERNAL_SERVER_ERROR)
  def convert_audio_to_text(self, audio_file_path):
    model = whisper.load_model('tiny')
    result = model.transcribe(audio_file_path)
    return result['text']