"""
Portfolio application Django admin configuration.

This module configures the Django admin interface for portfolio management including:
- Skill administration with category and proficiency filtering
- Project administration with inline image management
- Advanced filtering, search, and organization features
- Fieldset organization for better user experience
"""

from django.contrib import admin
from .models import Skill, Project, ProjectImage


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    """
    Django admin configuration for the Skill model.
    
    Provides comprehensive skill management with:
    - List display showing key skill information
    - Filtering by category and proficiency level
    - Search functionality across skill names
    - Organized ordering by category and name
    
    This admin interface allows administrators to:
    - Add new technical skills and competencies
    - Categorize skills (frontend, backend, database, tools)
    - Set proficiency levels for each skill
    - Quickly find and manage existing skills
    """
    list_display = ['name', 'category', 'proficiency', 'created_at']
    list_filter = ['category', 'proficiency']
    search_fields = ['name']
    ordering = ['category', 'name']


class ProjectImageInline(admin.TabularInline):
    """
    Inline admin configuration for ProjectImage model.
    
    Allows management of additional project images directly within
    the Project admin interface. Provides:
    - Tabular inline display for efficient image management
    - Image upload, caption, and ordering fields
    - Extra empty form for adding new images
    
    This inline interface enables administrators to:
    - Add multiple images to projects for galleries
    - Set captions for accessibility and context
    - Control display order of images
    - Manage project galleries without leaving the project edit page
    """
    model = ProjectImage
    extra = 1
    fields = ['image', 'caption', 'order']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """
    Django admin configuration for the Project model.
    
    Provides comprehensive project management with:
    - Organized fieldsets for logical data entry
    - Advanced filtering and search capabilities
    - Inline image management for project galleries
    - Technology association through filter_horizontal widget
    - Automatic slug generation from project title
    
    Features:
    - List display with key project information and status
    - Filtering by featured status, technology categories, and dates
    - Full-text search across titles and descriptions
    - Fieldsets organized by: Basic Info, Media, Links, Technologies, Settings
    - Inline management of additional project images
    - Horizontal filter widget for easy technology selection
    
    This admin interface allows administrators to:
    - Create and manage portfolio projects
    - Associate projects with relevant technologies/skills
    - Upload main project images and additional gallery images
    - Set featured status for homepage highlights
    - Organize projects with automatic slug generation
    - Add GitHub and live demo URLs
    """
    list_display = ['title', 'featured', 'created_at', 'updated_at']
    list_filter = ['featured', 'technologies__category', 'created_at']
    search_fields = ['title', 'description']
    prepopulated_fields = {'slug': ('title',)}
    filter_horizontal = ['technologies']
    inlines = [ProjectImageInline]
    ordering = ['-featured', '-created_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('title', 'slug', 'description', 'detailed_description')
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Links', {
            'fields': ('github_url', 'live_url')
        }),
        ('Technologies', {
            'fields': ('technologies',)
        }),
        ('Settings', {
            'fields': ('featured',)
        }),
    )
