from django.contrib import admin
from .models import ContactMessage, Newsletter


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
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
        queryset.update(status='read')
        self.message_user(request, f"{queryset.count()} messages marked as read.")
    mark_as_read.short_description = "Mark selected messages as read"
    
    def mark_as_replied(self, request, queryset):
        queryset.update(status='replied')
        self.message_user(request, f"{queryset.count()} messages marked as replied.")
    mark_as_replied.short_description = "Mark selected messages as replied"
    
    def archive_messages(self, request, queryset):
        queryset.update(status='archived')
        self.message_user(request, f"{queryset.count()} messages archived.")
    archive_messages.short_description = "Archive selected messages"


@admin.register(Newsletter)
class NewsletterAdmin(admin.ModelAdmin):
    list_display = ['email', 'name', 'is_active', 'subscribed_at']
    list_filter = ['is_active', 'subscribed_at']
    search_fields = ['email', 'name']
    ordering = ['-subscribed_at']
    readonly_fields = ['ip_address', 'subscribed_at']
    actions = ['activate_subscriptions', 'deactivate_subscriptions']
    
    def activate_subscriptions(self, request, queryset):
        queryset.update(is_active=True)
        self.message_user(request, f"{queryset.count()} subscriptions activated.")
    activate_subscriptions.short_description = "Activate selected subscriptions"
    
    def deactivate_subscriptions(self, request, queryset):
        queryset.update(is_active=False)
        self.message_user(request, f"{queryset.count()} subscriptions deactivated.")
    deactivate_subscriptions.short_description = "Deactivate selected subscriptions"
