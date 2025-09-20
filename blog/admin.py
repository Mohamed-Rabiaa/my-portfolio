"""
Django admin configuration for the blog application.

This module defines the admin interface customizations for blog models,
providing enhanced management capabilities for content creators and
administrators. Includes custom admin classes with:
- Optimized list displays and filtering
- Search functionality across relevant fields
- Bulk actions for content management
- Organized fieldsets for better UX
- Automatic slug generation and author assignment
"""

from django.contrib import admin
from .models import Category, Tag, BlogPost, Comment


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    Admin configuration for Category model.
    
    Provides a streamlined interface for managing blog categories with
    automatic slug generation and search capabilities. Categories help
    organize blog content and improve navigation.
    
    Features:
        - List display showing name, slug, and creation date
        - Automatic slug generation from category name
        - Search functionality by category name
    """
    list_display = ['name', 'slug', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    """
    Admin configuration for Tag model.
    
    Provides management interface for blog tags with automatic slug
    generation and search capabilities. Tags offer granular content
    labeling and support multiple assignments per post.
    
    Features:
        - List display showing name, slug, and creation date
        - Automatic slug generation from tag name
        - Search functionality by tag name
    """
    list_display = ['name', 'slug', 'created_at']
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ['name']


@admin.register(BlogPost)
class BlogPostAdmin(admin.ModelAdmin):
    """
    Comprehensive admin configuration for BlogPost model.
    
    Provides a feature-rich interface for managing blog posts with advanced
    filtering, search, and organization capabilities. Includes automatic
    author assignment and organized fieldsets for improved content creation
    workflow.
    
    Features:
        - Comprehensive list display with key post information
        - Advanced filtering by status, category, tags, and dates
        - Full-text search across title, excerpt, and content
        - Automatic slug generation from post title
        - Horizontal filter widget for tag selection
        - Organized fieldsets for logical content grouping
        - Date hierarchy navigation by publication date
        - Automatic author assignment for new posts
    """
    list_display = ['title', 'author', 'category', 'status', 'featured', 'views', 'published_at']
    list_filter = ['status', 'featured', 'category', 'tags', 'created_at', 'published_at']
    search_fields = ['title', 'excerpt', 'content']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['tags']
    ordering = ['-created_at']
    date_hierarchy = 'published_at'
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'excerpt', 'content')
        }),
        ('Media', {
            'fields': ('featured_image',)
        }),
        ('Classification', {
            'fields': ('category', 'tags')
        }),
        ('Publishing', {
            'fields': ('author', 'status', 'published_at')
        }),
        ('Settings', {
            'fields': ('featured', 'read_time')
        }),
        ('Statistics', {
            'fields': ('views',),
            'classes': ('collapse',)
        }),
    )
    
    def save_model(self, request, obj, form, change):
        """
        Override save_model to automatically assign author for new posts.
        
        When creating a new blog post, automatically sets the current user
        as the author. This ensures proper attribution and eliminates the
        need for manual author selection during content creation.
        
        Args:
            request: HTTP request object containing user information
            obj: BlogPost model instance being saved
            form: Admin form instance
            change: Boolean indicating if this is an update (True) or creation (False)
        """
        if not change:  # If creating new object
            obj.author = request.user
        super().save_model(request, obj, form, change)


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    """
    Admin configuration for Comment model with moderation capabilities.
    
    Provides comprehensive comment management with bulk moderation actions
    and advanced filtering. Supports content moderation workflow to maintain
    quality and prevent spam while enabling community engagement.
    
    Features:
        - List display showing commenter, post, approval status, and date
        - Filtering by approval status and creation date
        - Search across commenter details and post titles
        - Bulk approval and disapproval actions
        - Chronological ordering (newest first)
        - Admin feedback messages for bulk actions
    """
    list_display = ['name', 'post', 'approved', 'created_at']
    list_filter = ['approved', 'created_at']
    search_fields = ['name', 'email', 'content', 'post__title']
    ordering = ['-created_at']
    actions = ['approve_comments', 'disapprove_comments']
    
    def approve_comments(self, request, queryset):
        """
        Bulk action to approve selected comments.
        
        Marks selected comments as approved, making them visible to site
        visitors. Provides feedback to the admin about the number of
        comments processed.
        
        Args:
            request: HTTP request object
            queryset: QuerySet of selected Comment instances
        """
        queryset.update(approved=True)
        self.message_user(request, f"{queryset.count()} comments approved.")
    approve_comments.short_description = "Approve selected comments"
    
    def disapprove_comments(self, request, queryset):
        """
        Bulk action to disapprove selected comments.
        
        Marks selected comments as not approved, hiding them from site
        visitors. Useful for moderating inappropriate content or spam.
        Provides feedback about the number of comments processed.
        
        Args:
            request: HTTP request object
            queryset: QuerySet of selected Comment instances
        """
        queryset.update(approved=False)
        self.message_user(request, f"{queryset.count()} comments disapproved.")
    disapprove_comments.short_description = "Disapprove selected comments"
