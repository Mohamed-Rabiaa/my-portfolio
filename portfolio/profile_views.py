"""
API views for UserProfile model.

This module provides API endpoints for accessing user profile information,
specifically designed to serve the admin's profile data to the frontend.
"""

from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.contrib.auth.models import User
from django.shortcuts import get_object_or_404
from .profile import UserProfile
from .profile_serializers import AdminProfileSerializer, UserProfileSerializer


@api_view(['GET'])
def admin_profile(request):
    """
    Get the admin user's profile information.
    
    This endpoint returns the profile information of the first superuser
    (admin) in the system, which is typically used for displaying
    the site owner's information on the frontend.
    
    Returns:
        Response: JSON containing admin profile data including photo URL
    """
    try:
        # Get the first superuser (admin)
        admin_user = User.objects.filter(is_superuser=True).first()
        
        if not admin_user:
            return Response(
                {'error': 'No admin user found'}, 
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Get or create the admin's profile
        profile, created = UserProfile.objects.get_or_create(user=admin_user)
        
        serializer = AdminProfileSerializer(profile, context={'request': request})
        return Response(serializer.data)
        
    except Exception as e:
        return Response(
            {'error': 'Failed to retrieve admin profile'}, 
            status=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


class UserProfileDetailView(generics.RetrieveUpdateAPIView):
    """
    Retrieve and update user profile information.
    
    This view allows authenticated users to view and update their
    own profile information.
    """
    serializer_class = UserProfileSerializer
    
    def get_object(self):
        """Get the current user's profile."""
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile


class AdminProfileDetailView(generics.RetrieveAPIView):
    """
    Retrieve admin profile information.
    
    This view provides detailed admin profile information
    for frontend display purposes.
    """
    serializer_class = AdminProfileSerializer
    
    def get_object(self):
        """Get the admin user's profile."""
        admin_user = get_object_or_404(User, is_superuser=True)
        profile, created = UserProfile.objects.get_or_create(user=admin_user)
        return profile