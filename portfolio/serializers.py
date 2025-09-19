from rest_framework import serializers
from .models import Project, Skill, ProjectImage


class SkillSerializer(serializers.ModelSerializer):
    """Serializer for Skill model"""
    category_display = serializers.CharField(source='get_category_display', read_only=True)
    proficiency_display = serializers.CharField(source='get_proficiency_display', read_only=True)

    class Meta:
        model = Skill
        fields = ['id', 'name', 'category', 'category_display', 'proficiency', 'proficiency_display', 'created_at']


class ProjectImageSerializer(serializers.ModelSerializer):
    """Serializer for ProjectImage model"""
    
    class Meta:
        model = ProjectImage
        fields = ['id', 'image', 'caption', 'order']


class ProjectSerializer(serializers.ModelSerializer):
    """Serializer for Project model"""
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
    """Simplified serializer for project list view"""
    technologies = serializers.StringRelatedField(many=True, read_only=True)
    
    class Meta:
        model = Project
        fields = [
            'id', 'title', 'slug', 'description', 'technologies',
            'github_url', 'live_url', 'image', 'featured', 'created_at'
        ]