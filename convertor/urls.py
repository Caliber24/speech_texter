from rest_framework import routers

from .views import VTTViewSet


vtt_router = routers.DefaultRouter()
vtt_router.register('voice-to-text', VTTViewSet, basename='voice-to-text')

urlpatterns = vtt_router.urls
