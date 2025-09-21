"""
Contact Admin Module

This module contains Django admin configurations for the contact application.
It provides admin interfaces for managing contact messages and newsletter subscriptions
with custom actions and organized fieldsets.

Classes:
    ContactMessageAdmin: Admin configuration for ContactMessage model
    NewsletterAdmin: Admin configuration for Newsletter model

Author: Your Name
Version: 1.0.0
"""

from django.contrib import admin
from .models import ContactMessage, Newsletter


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    """
    Django admin configuration for ContactMessage model.
    
    Provides a comprehensive interface for managing contact messages with
    filtering, searching, and bulk actions for message status management.
    
    Attributes:
        list_display (list): Fields to display in the admin list view
        list_filter (list): Fields to filter by in the admin interface
        search_fields (list): Fields to search through
        ordering (list): Default ordering for the list view
        readonly_fields (list): Fields that cannot be edited
        actions (list): Custom admin actions available
        fieldsets (tuple): Organized field groupings for the detail view
    """
    
    list_display = ['name', 'email', 'subject', 'status', 'created_at']
    list_filter = ['subject', 'status', 'created_at']
    search_fields = ['name', 'email', 'message', 'company']
    ordering = ['-created_at']
    readonly_fields = ['ip_address', 'user_agent', 'created_at']
    actions = ['mark_as_read', 'mark_as_replied', 'archive_messages']
    
    fieldsets = (
        ('Contact Information', {
            'fields': ('name', 'email', 'phone', 'company')
        }),
        ('Message Details', {
            'fields': ('subject', 'message')
        }),
        ('Status', {
            'fields': ('status',)
        }),
        ('Technical Information', {
            'fields': ('ip_address', 'user_agent', 'created_at'),
            'classes': ('collapse',)
        }),
    )
    
    def mark_as_read(self, request, queryset):
        """
        Admin action to mark selected contact messages as read.
        
        Args:
            request: The HTTP request object
            queryset: QuerySet of selected ContactMessage objects
            
        Returns:
            None: Updates message status and displays success message
        """
        queryset.update(status='read')
        self.message_user(request, f"{queryset.count()} messages marked as read.")
    mark_as_read.short_description = "Mark selected messages as read"
    
    def mark_as_replied(self, request, queryset):
        """
        Admin action to mark selected contact messages as replied.
        
        Args:
            request: The HTTP request object
            queryset: QuerySet of selected ContactMessage objects
            
        Returns:
            None: Updates message status and displays success message
        """
        queryset.update(status='replied')
        self.message_user(request, f"{queryset.count()} messages marked as replied.")
    mark_as_replied.short_description = "Mark selected messages as replied"
    
    def archive_messages(self, request, queryset):
        """
        Admin action to archive selected contact messages.
        
        Args:
            request: The HTTP request object
            queryset: QuerySet of selected ContactMessage objects
            
        Returns:
            None: Updates message status to archived and displays success message
        """
        queryset.update(status='archived')
        self.message_user(request, f"{queryset.count()} messages archived.")
    archive_messages.short_description = "Archive selected messages"


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    """
    Django admin configuration for Newsletter model.
    
    Provides an interface for managing newsletter subscriptions with
    filtering, searching, and bulk actions for subscription management.
    
    Attributes:
        list_display (list): Fields to display in the admin list view
        list_filter (list): Fields to filter by in the admin interface
        search_fields (list): Fields to search through
        ordering (list): Default ordering for the list view
        readonly_fields (list): Fields that cannot be edited
        actions (list): Custom admin actions available
    """
    
    list_display = ['email', 'name', 'is_active', 'subscribed_at']
    list_filter = ['is_active', 'subscribed_at']
    search_fields = ['email', 'name']
    ordering = ['-subscribed_at']
    readonly_fields = ['ip_address', 'subscribed_at']
    actions = ['activate_subscriptions', 'deactivate_subscriptions']
    
    def activate_subscriptions(self, request, queryset):
        """
        Admin action to activate selected newsletter subscriptions.
        
        Args:
            request: The HTTP request object
            queryset: QuerySet of selected Newsletter objects
            
        Returns:
            None: Activates subscriptions and displays success message
        """
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} subscriptions activated.")
    activate_subscriptions.short_description = "Activate selected subscriptions"
    
    def deactivate_subscriptions(self, request, queryset):
        """
        Admin action to deactivate selected newsletter subscriptions.
        
        Args:
            request: The HTTP request object
            queryset: QuerySet of selected Newsletter objects
            
        Returns:
            None: Deactivates subscriptions and displays success message
        """
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} subscriptions deactivated.")
    deactivate_subscriptions.short_description = "Deactivate selected subscriptions"
