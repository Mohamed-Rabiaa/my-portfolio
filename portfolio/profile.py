"""
User profile model for extending Django's built-in User model.

This module defines a UserProfile model that extends the default User model
with additional fields like profile photo, maintaining a one-to-one relationship.
"""

from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class UserProfile(models.Model):
    """
    User profile model that extends the built-in User model.
    
    This model maintains a one-to-one relationship with Django's User model
    and adds additional fields like profile photo, contact information, and social media links.
    
    Attributes:
        user (OneToOneField): Link to Django's User model
        profile_photo (ImageField): User's profile photo
        bio (TextField): Optional user biography
        phone (CharField): Contact phone number
        location (CharField): Current location (city, country)
        linkedin_url (URLField): LinkedIn profile URL
        github_url (URLField): GitHub profile URL
        twitter_url (URLField): Twitter/X profile URL
        created_at (DateTimeField): When the profile was created
        updated_at (DateTimeField): When the profile was last updated
    """
    user = models.OneToOneField(
        User, 
        on_delete=models.CASCADE,
        related_name='profile'
    )
    profile_photo = models.ImageField(
        upload_to='profile_photos/',
        blank=True,
        null=True,
        help_text="Upload your profile photo"
    )
    bio = models.TextField(
        blank=True,
        help_text="Brief biography or description"
    )
    phone = models.CharField(
        max_length=20,
        blank=True,
        help_text="Contact phone number"
    )
    location = models.CharField(
        max_length=100,
        blank=True,
        help_text="Current location (city, country)"
    )
    linkedin_url = models.URLField(
        blank=True,
        help_text="LinkedIn profile URL"
    )
    github_url = models.URLField(
        blank=True,
        help_text="GitHub profile URL"
    )
    twitter_url = models.URLField(
        blank=True,
        help_text="Twitter profile URL"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "User Profile"
        verbose_name_plural = "User Profiles"

    def __str__(self):
        return f"{self.user.username}'s Profile"

    @property
    def profile_photo_url(self):
        """Return the URL of the profile photo if it exists."""
        if self.profile_photo and hasattr(self.profile_photo, 'url'):
            return self.profile_photo.url
        return None


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Signal receiver to automatically create a UserProfile when a User is created.
    """
    if created:
        UserProfile.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Signal receiver to save the UserProfile when the User is saved.
    """
    if hasattr(instance, 'profile'):
        instance.profile.save()