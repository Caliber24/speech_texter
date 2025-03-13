from rest_framework import serializers
from .models import VTT
from .validators import validate_audio_file
class VTTSerializer(serializers.ModelSerializer):
  audio = serializers.FileField(validators=[validate_audio_file], help_text='Upload file in here', write_only=True)
  class Meta:
    model = VTT
    fields = ['id','title', 'user', 'audio', 'transcript', 'created_at']
    read_only_fields = ['user', 'transcript']
    
    
    def create(self, validated_data):
      audio_file = validated_data.pop('audio', None)
      print("chiiiie" + validated_data)
      instance = VTT.objects.create(**validated_data)
      return instance
