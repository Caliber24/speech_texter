from rest_framework import serializers
from .models import VTT
from .validators import validate_audio_file

class VTTSerializer(serializers.ModelSerializer):
    audio = serializers.FileField(validators=[validate_audio_file], help_text='Upload file in here', write_only=True)
    title = serializers.CharField(max_length=255, required=True)
    created_at = serializers.DateTimeField(read_only=True)
    user_id = serializers.CharField(source='user.id', read_only=True)
    
    class Meta:
        model = VTT
        fields = ['id', 'title', 'user_id', 'audio', 'transcript', 'created_at']
        read_only_fields = ['user_id', 'transcript', 'created_at']
    
    def create(self, validated_data):
        audio_file = validated_data.pop('audio', None)
        instance = VTT.objects.create(**validated_data)
        return instance
