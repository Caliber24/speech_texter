import os
from email.policy import default

import boto3
from rest_framework.viewsets import ModelViewSet, GenericViewSet, mixins, generics
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from .serializers import VTTSerializer
from .models import VTT
import uuid
from botocore.client import Config
from django.core.files.storage import default_storage
from .convertor import transcribe_audio
from django.conf import settings
import os

# set Liara Bucket Conf
LIARA = {
    'endpoint': settings.LIARA_ENDPOINT,
    'accesskey': settings.LIARA_ACCESS_KEY,
    'secretkey': settings.LIARA_SECRET_KEY,
    'bucket': settings.LIARA_BUCKET_NAME
}


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
        audio_file = serializer.validated_data['audio']
        print(audio_file)
        file_name = f'{uuid.uuid4()}{os.path.splitext(audio_file.name)[1]}'
        s3 = boto3.client('s3', endpoint_url=LIARA['endpoint'], aws_access_key_id=LIARA['accesskey'],
                          aws_secret_access_key=LIARA['secretkey'],
                          config=Config(signature_version='s3v4', s3={'addressing_style': 'path'}, region_name='default'))
        try:
            s3.put_object(Bucket=LIARA['bucket'], Key=file_name, Body=audio_file.read(), ACL='public-read')
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        file_path = f'{LIARA["endpoint"]}/{LIARA["bucket"]}/{file_name}'
        transcription = transcribe_audio(file_path)
        vtt_instance = serializer.save(user=request.user, audio=file_name, transcript=transcription)
        return Response(VTTSerializer(vtt_instance).data, status=status.HTTP_201_CREATED)
