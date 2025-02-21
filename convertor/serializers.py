from rest_framework import serializers
from .models import VTT
class VTTSerializer(serializers.ModelSerializer):
  class Meta:
    model = VTT
    fields = ['id', 'user', 'audio_path', 'transcript', 'created_at']
    read_only_fields = ['user', 'transcript']
    
    
    