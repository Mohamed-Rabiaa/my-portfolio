"""
Contact Application Admin Configuration

This module configures the Django admin interface for the contact application,
providing comprehensive management tools for contact messages and newsletter
subscriptions with enhanced workflow actions and organized fieldsets.
"""

from django.contrib import admin
from .models import ContactMessage, Newsletter


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    """
    Admin configuration for ContactMessage model with comprehensive management features.
    
    This admin class provides a full-featured interface for managing contact form
    submissions with organized fieldsets, filtering options, search capabilities,
    and custom actions for message workflow management.
    
    Features:
    - Organized fieldsets for better data presentation
    - Advanced filtering by subject, status, and date
    - Search across name, email, message, and company fields
    - Custom actions for status management (read, replied, archived)
    - Read-only technical fields for security information
    - Chronological ordering with newest messages first
    
    Actions:
    - mark_as_read: Mark messages as read for tracking
    - mark_as_replied: Mark messages as replied after response
    - archive_messages: Archive old or resolved messages
    
    Fieldsets:
    - Contact Information: Personal and company details
    - Message Details: Subject and message content
    - Status: Current processing status
    - Technical Information: IP address and user agent (collapsed)
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
        Mark selected contact messages as read.
        
        This action updates the status of selected messages to 'read',
        indicating they have been reviewed by an administrator.
        
        Args:
            request: The HTTP request object
            queryset: QuerySet of selected ContactMessage instances
        """
        queryset.update(status='read')
        self.message_user(request, f"{queryset.count()} messages marked as read.")
    mark_as_read.short_description = "Mark selected messages as read"
    
    def mark_as_replied(self, request, queryset):
        """
        Mark selected contact messages as replied.
        
        This action updates the status of selected messages to 'replied',
        indicating a response has been sent to the contact person.
        
        Args:
            request: The HTTP request object
            queryset: QuerySet of selected ContactMessage instances
        """
        queryset.update(status='replied')
        self.message_user(request, f"{queryset.count()} messages marked as replied.")
    mark_as_replied.short_description = "Mark selected messages as replied"
    
    def archive_messages(self, request, queryset):
        """
        Archive selected contact messages.
        
        This action updates the status of selected messages to 'archived',
        moving them out of active workflow while preserving the data.
        
        Args:
            request: The HTTP request object
            queryset: QuerySet of selected ContactMessage instances
        """
        queryset.update(status='archived')
        self.message_user(request, f"{queryset.count()} messages archived.")
    archive_messages.short_description = "Archive selected messages"


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    """
    Admin configuration for Newsletter model with subscription management features.
    
    This admin class provides tools for managing newsletter subscriptions with
    filtering, search capabilities, and bulk actions for subscription status
    management. It includes read-only fields for security and audit purposes.
    
    Features:
    - List display with key subscription information
    - Filtering by subscription status and date
    - Search by email and subscriber name
    - Custom actions for bulk subscription management
    - Read-only technical fields for audit trail
    - Chronological ordering with newest subscriptions first
    
    Actions:
    - activate_subscriptions: Reactivate inactive subscriptions
    - deactivate_subscriptions: Deactivate active subscriptions
    
    Use Cases:
    - Managing newsletter subscriber lists
    - Handling unsubscribe requests
    - Monitoring subscription trends
    - Maintaining data integrity and audit trails
    """
    list_display = ['email', 'name', 'is_active', 'subscribed_at']
    list_filter = ['is_active', 'subscribed_at']
    search_fields = ['email', 'name']
    ordering = ['-subscribed_at']
    readonly_fields = ['ip_address', 'subscribed_at']
    actions = ['activate_subscriptions', 'deactivate_subscriptions']
    
    def activate_subscriptions(self, request, queryset):
        """
        Activate selected newsletter subscriptions.
        
        This action reactivates inactive newsletter subscriptions, allowing
        subscribers to receive newsletters again. Useful for handling
        re-subscription requests or correcting accidental deactivations.
        
        Args:
            request: The HTTP request object
            queryset: QuerySet of selected Newsletter instances
        """
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} subscriptions activated.")
    activate_subscriptions.short_description = "Activate selected subscriptions"
    
    def deactivate_subscriptions(self, request, queryset):
        """
        Deactivate selected newsletter subscriptions.
        
        This action deactivates active newsletter subscriptions, stopping
        newsletter delivery to selected subscribers. Useful for handling
        unsubscribe requests or managing inactive accounts.
        
        Args:
            request: The HTTP request object
            queryset: QuerySet of selected Newsletter instances
        """
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} subscriptions deactivated.")
    deactivate_subscriptions.short_description = "Deactivate selected subscriptions"
