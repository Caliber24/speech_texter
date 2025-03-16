from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import VTT
from .views import VTTViewSet
from django.test import RequestFactory
from rest_framework.test import force_authenticate

User = get_user_model()

class DuplicateTitleTestCase(TestCase):
    def setUp(self):
        # Create a test user
        self.user = User.objects.create_user(
            imei='123456789012345',
            password='testpassword'
        )
        
        # Create some VTT instances with titles
        VTT.objects.create(
            user=self.user,
            title="Test Title",
            transcript="This is a test transcript"
        )
        
        VTT.objects.create(
            user=self.user,
            title="Test Title (1)",
            transcript="This is another test transcript"
        )
        
        # Set up request factory
        self.factory = RequestFactory()
        
    def test_get_unique_title(self):
        """Test the _get_unique_title method in VTTViewSet"""
        viewset = VTTViewSet()
        
        # Test with a new title
        new_title = "New Title"
        unique_title = viewset._get_unique_title(new_title, self.user)
        self.assertEqual(unique_title, new_title)
        
        # Test with an existing title
        existing_title = "Test Title"
        unique_title = viewset._get_unique_title(existing_title, self.user)
        self.assertEqual(unique_title, "Test Title (2)")
        
        # Test with an existing title that already has a number
        existing_title_with_number = "Test Title (1)"
        unique_title = viewset._get_unique_title(existing_title_with_number, self.user)
        self.assertEqual(unique_title, "Test Title (2)")
