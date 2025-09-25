"""
Serializers for UserProfile model.

This module provides DRF serializers for the UserProfile model,
enabling API access to user profile information including profile photos.
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .profile import UserProfile


class UserProfileSerializer(serializers.ModelSerializer):
    """
    Serializer for UserProfile model.
    
    Provides serialization for user profile data including
    profile photo URL and user information.
    """
    username = serializers.CharField(source='user.username', read_only=True)
    first_name = serializers.CharField(source='user.first_name', read_only=True)
    last_name = serializers.CharField(source='user.last_name', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)
    profile_photo_url = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfile
        fields = [
            'id',
            'username',
            'first_name', 
            'last_name',
            'email',
            'profile_photo',
            'profile_photo_url',
            'bio',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_profile_photo_url(self, obj):
        """
        Get the full URL for the profile photo.
        """
        if obj.profile_photo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile_photo.url)
            return obj.profile_photo.url
        return None


class AdminProfileSerializer(serializers.ModelSerializer):
    """
    Simplified serializer for admin profile information.
    
    This serializer is specifically designed to return the admin's
    profile information for display on the frontend.
    """
    full_name = serializers.SerializerMethodField()
    profile_photo_url = serializers.SerializerMethodField()
    
    class Meta:
        model = UserProfile
        fields = [
            'full_name',
            'profile_photo_url',
            'bio'
        ]
    
    def get_full_name(self, obj):
        """Get the user's full name."""
        if obj.user.first_name and obj.user.last_name:
            return f"{obj.user.first_name} {obj.user.last_name}"
        return obj.user.username
    
    def get_profile_photo_url(self, obj):
        """Get the full URL for the profile photo."""
        if obj.profile_photo:
            request = self.context.get('request')
            if request:
                return request.build_absolute_uri(obj.profile_photo.url)
            return obj.profile_photo.url
        return None