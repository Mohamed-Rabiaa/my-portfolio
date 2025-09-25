"""
Django admin configuration for UserProfile model.

This module provides admin interface customizations for managing user profiles,
including profile photo uploads and user information management.
"""

from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import User
from .profile import UserProfile


class UserProfileInline(admin.StackedInline):
    """
    Inline admin for UserProfile model.
    
    This allows editing the user profile information directly
    from the User admin page.
    """
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile'
    fields = ('profile_photo', 'bio')


class UserAdmin(BaseUserAdmin):
    """
    Extended User admin that includes profile information.
    
    This admin class extends Django's default UserAdmin to include
    the UserProfile inline, allowing administrators to manage
    user profile photos and bio information directly from the
    user edit page.
    """
    inlines = (UserProfileInline,)
    
    def get_inline_instances(self, request, obj=None):
        """
        Override to ensure UserProfile exists for the user.
        """
        if not obj:
            return []
        return super().get_inline_instances(request, obj)


# Unregister the default User admin and register our custom one
admin.site.unregister(User)
admin.site.register(User, UserAdmin)


@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    """
    Standalone admin for UserProfile model.
    
    This provides a separate admin interface for managing user profiles
    if needed, though the inline approach is preferred.
    """
    list_display = ('user', 'created_at', 'updated_at')
    list_filter = ('created_at', 'updated_at')
    search_fields = ('user__username', 'user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('User Information', {
            'fields': ('user',)
        }),
        ('Profile Details', {
            'fields': ('profile_photo', 'bio')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )