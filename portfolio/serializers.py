"""
Portfolio application serializers for API data transformation.

This module provides serializers for the portfolio functionality including:
- Project serialization with nested technologies and images
- Skill serialization with display names for categories and proficiency
- Project image serialization for gallery functionality
- Optimized list serializers for performance in listing views
"""

from rest_framework import serializers
from .models import Project, Skill, ProjectImage


class SkillSerializer(serializers.ModelSerializer):
    """
    Serializer for the Skill model with enhanced display fields.
    
    Provides comprehensive skill information including:
    - Basic skill details (name, category, proficiency)
    - Human-readable display names for category and proficiency levels
    - Creation timestamp for tracking
    
    The display fields use Django's get_FOO_display() methods to provide
    user-friendly names instead of database values (e.g., 'Frontend Development'
    instead of 'frontend').
    
    Fields:
        id: Unique skill identifier
        name: Skill name (e.g., 'React', 'Python')
        category: Raw category value
        category_display: Human-readable category name
        proficiency: Raw proficiency level
        proficiency_display: Human-readable proficiency level
        created_at: Skill creation timestamp
    """
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    proficiency_display = serializers.CharField(source='get_proficiency_display', read_only=True)

    class Meta:
        model = Skill
        fields = ['id', 'name', 'category', 'category_display', 'proficiency', 'proficiency_display', 'created_at']


class ProjectImageSerializer(serializers.ModelSerializer):
    """
    Serializer for the ProjectImage model for gallery functionality.
    
    Handles additional project images beyond the main project image.
    Provides support for:
    - Image file handling and URLs
    - Optional captions for accessibility and context
    - Ordering for consistent gallery display
    
    This serializer is typically used nested within ProjectSerializer
    to provide complete project galleries.
    
    Fields:
        id: Unique image identifier
        image: Image file URL
        caption: Optional image description
        order: Display order for gallery sorting
    """
    
    class Meta:
        model = ProjectImage
        fields = ['id', 'image', 'caption', 'order']


class ProjectSerializer(serializers.ModelSerializer):
    """
    Comprehensive serializer for the Project model with full details.
    
    Provides complete project information including:
    - All project fields and metadata
    - Nested technologies with full skill details
    - Additional images for project galleries
    - All URLs and links (GitHub, live demo)
    
    This serializer is used for detailed project views where all
    information is needed. For list views, use ProjectListSerializer
    for better performance.
    
    Nested Data:
        technologies: Full SkillSerializer objects for each technology
        additional_images: ProjectImageSerializer objects for gallery
    
    Fields:
        id: Unique project identifier
        title: Project title
        slug: URL-friendly project identifier
        description: Brief project description
        detailed_description: Full project details
        technologies: Associated skills/technologies (nested)
        github_url: GitHub repository URL
        live_url: Live demo URL
        image: Main project image
        featured: Featured status flag
        additional_images: Gallery images (nested)
        created_at: Project creation timestamp
        updated_at: Last modification timestamp
    """
    technologies = SkillSerializer(many=True, read_only=True)
    additional_images = ProjectImageSerializer(many=True, read_only=True)
    
    class Meta:
        model = Project
        fields = [
            'id', 'title', 'slug', 'description', 'detailed_description',
            'technologies', 'github_url', 'live_url', 'image', 'featured',
            'additional_images', 'created_at', 'updated_at'
        ]


class ProjectListSerializer(serializers.ModelSerializer):
    """
    Optimized serializer for project list views with minimal data.
    
    Provides essential project information for list displays while
    maintaining performance by:
    - Using string representation for technologies instead of nested objects
    - Excluding detailed descriptions and additional images
    - Including only fields necessary for list/card displays
    
    This serializer is ideal for:
    - Project listing pages
    - Portfolio overview sections
    - Search results
    - API endpoints with many projects
    
    Performance Benefits:
        - Reduced database queries through simplified technology field
        - Smaller response payload
        - Faster serialization for large project lists
    
    Fields:
        id: Unique project identifier
        title: Project title
        slug: URL-friendly project identifier
        description: Brief project description
        technologies: Technology names as strings (not nested objects)
        github_url: GitHub repository URL
        live_url: Live demo URL
        image: Main project image
        featured: Featured status flag
        created_at: Project creation timestamp
    """
    technologies = serializers.StringRelatedField(many=True, read_only=True)
    
    class Meta:
        model = Project
        fields = [
            'id', 'title', 'slug', 'description', 'technologies',
            'github_url', 'live_url', 'image', 'featured', 'created_at'
        ]