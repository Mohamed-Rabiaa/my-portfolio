from django.contrib import admin
from .models import Skill, Project, ProjectImage


@admin.register(Skill)
class SkillAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'proficiency', 'created_at']
    list_filter = ['category', 'proficiency']
    search_fields = ['name']
    ordering = ['category', 'name']


class ProjectImageInline(admin.TabularInline):
    model = ProjectImage
    extra = 1
    fields = ['image', 'caption', 'order']


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
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
