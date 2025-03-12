from rest_framework import serializers
from djoser.serializers import  TokenCreateSerializer as BaseTokenCreateSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from .models import User

class CustomUserSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ['imei', 'is_active', 'is_admin']


class CustomUserCreateSerializer(serializers.ModelSerializer):
  class Meta:
    model = User
    fields = ['imei']
    extra_kwargs = {}
  
  def validate(self, attrs):
    if 'password' not in attrs:
      attrs['password'] = None
    return attrs
  
  def create(self, validated_data):
    password = validated_data.pop('password', None)
    user = User.objects.create_user(imei=validated_data['imei'], password=password)
    serializers = CustomUserCreateSerializer(user)
    return serializers.data
  

class CustomTokenCreateSerializer(serializers.Serializer):
    imei = serializers.CharField()
    def validate(self, attrs):
      imei = attrs.get('imei')
      try:
        user = User.objects.get(imei=imei)
      except User.DoesNotExist:
        raise serializers.ValidationError('User with this IMEI does not exist.')
      
      refresh = RefreshToken.for_user(user)

      return{
        'refresh': str(refresh),
        'access': str(refresh.access_token)
      }
      