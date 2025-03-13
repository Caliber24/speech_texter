from django.contrib.auth.backends import ModelBackend
from django.contrib.auth import get_user_model

class CustomAuthBackend(ModelBackend):
  def authenticate(self, request, imei=None, password=None):
    if imei:
      try:
        user = get_user_model().objects.get(imei=imei)
        if password:
          if user.check_password(password):
            return user
        else:
          return user
      except get_user_model().DoesNotExist:
        return None
    return None
  
  def get_user(self, user_id):
    try:
      return get_user_model().objects.get(user_id=user_id)
    except get_user_model().DoesNotExist:
      return None