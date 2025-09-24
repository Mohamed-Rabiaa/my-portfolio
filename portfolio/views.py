"""
Portfolio application views for showcasing projects and skills.

This module provides REST API views for the portfolio functionality including:
- Project listing, detail viewing, and filtering
- Skill management and categorization
- Featured project highlights
- Portfolio statistics and analytics
- Skills organized by category for better presentation
"""

import logging
import time
from rest_framework import generics, filters
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Project, Skill
from .serializers import ProjectSerializer, ProjectListSerializer, SkillSerializer
from common.versioning import VersionCompatibilityMixin, deprecated_api
from common.pagination import BaseFilteredViewMixin, ProjectPagination
from common.monitoring import monitor_performance, PerformanceMonitor
from common.validators import ValidationMixin

# Initialize loggers
logger = logging.getLogger('portfolio')
performance_logger = logging.getLogger('performance')


class ProjectListView(ValidationMixin, BaseFilteredViewMixin, VersionCompatibilityMixin, generics.ListAPIView):
    """
    API view to list all portfolio projects with advanced filtering capabilities.
    
    Provides comprehensive project listing with support for:
    - Filtering by featured status and technology categories
    - Full-text search across project titles, descriptions, and technologies
    - Ordering by creation date or title
    - Featured projects displayed first for prominence
    - Date range filtering for project creation dates
    - Performance monitoring and metrics collection
    - Input validation and error handling
    
    This view is ideal for portfolio galleries, project archives, and
    filtered project displays based on specific technologies or criteria.
    """
    queryset = Project.objects.all()
    serializer_class = ProjectListSerializer
    pagination_class = ProjectPagination
    search_fields = ['title', 'description', 'technologies__name']
    filterset_fields = ['featured', 'technologies__category']
    ordering_fields = ['created_at', 'title']
    ordering = ['-featured', '-created_at']

    def list(self, request, *args, **kwargs):
        """Override list method to add performance monitoring."""
        with PerformanceMonitor('project_list_query'):
            return super().list(request, *args, **kwargs)


class ProjectDetailView(ValidationMixin, VersionCompatibilityMixin, generics.RetrieveAPIView):
    """
    API view to retrieve a single project by its slug.
    
    Provides detailed project information including:
    - Complete project description and details
    - Associated technologies and skills
    - Project links (GitHub, live demo)
    - Project images and gallery
    - All metadata and timestamps
    - Performance monitoring for detail views
    - Input validation and error handling
    
    Uses slug-based lookup for SEO-friendly URLs and better user experience.
    """
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    lookup_field = 'slug'

    def retrieve(self, request, *args, **kwargs):
        """Override retrieve method to add performance monitoring."""
        with PerformanceMonitor('project_detail_query'):
            return super().retrieve(request, *args, **kwargs)


class FeaturedProjectsView(ValidationMixin, generics.ListAPIView):
    """
    API view to list featured portfolio projects.
    
    Returns only projects marked as featured, typically used for:
    - Homepage project highlights
    - Featured work sections
    - Portfolio showcases
    - Performance monitoring for featured content
    - Input validation and error handling
    
    Projects are ordered by creation date (newest first) to show
    the most recent featured work prominently.
    """
    queryset = Project.objects.filter(featured=True)
    serializer_class = ProjectListSerializer

    def list(self, request, *args, **kwargs):
        """Override list method to add performance monitoring."""
        with PerformanceMonitor('featured_projects_query'):
            return super().list(request, *args, **kwargs)


class SkillListView(ValidationMixin, BaseFilteredViewMixin, generics.ListAPIView):
    """
    API view to list all portfolio skills with filtering capabilities.
    
    Provides comprehensive skill listing with support for:
    - Filtering by skill category (frontend, backend, tools, etc.)
    - Filtering by proficiency level (beginner, intermediate, advanced, expert)
    - Ordering by category and name for organized display
    - Date range filtering for skill acquisition dates
    - Performance monitoring and metrics collection
    - Input validation and error handling
    
    Skills are organized by category and proficiency to help visitors
    understand the developer's technical expertise and experience levels.
    """
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    filterset_fields = ['category', 'proficiency']
    ordering = ['category', 'name']

    def list(self, request, *args, **kwargs):
        """Override list method to add performance monitoring."""
        with PerformanceMonitor('skills_list_query'):
            return super().list(request, *args, **kwargs)


@api_view(['GET'])
@monitor_performance('portfolio.skills_by_category')
def skills_by_category(request):
    """
    API endpoint to retrieve skills organized by category.
    
    Returns a structured response with skills grouped by their categories
    (frontend, backend, database, tools, etc.) for organized display in
    portfolio skill sections.
    
    Response format:
    {
        "frontend": [list of frontend skills],
        "backend": [list of backend skills],
        "database": [list of database skills],
        ...
    }
    
    Each skill includes: id, name, proficiency, description, and icon.
    """
    with PerformanceMonitor('skills_by_category_query'):
        skills = Skill.objects.all().order_by('category', 'name')
        skills_by_category = {}
        
        for skill in skills:
            category = skill.category
            if category not in skills_by_category:
                skills_by_category[category] = []
            
            skills_by_category[category].append({
                'id': skill.id,
                'name': skill.name,
                'proficiency': skill.proficiency,
                'description': skill.description,
                'icon': skill.icon.url if skill.icon else None,
            })
        
        return Response(skills_by_category)


@api_view(['GET'])
@monitor_performance('portfolio.portfolio_stats')
def portfolio_stats(request):
    """
    API endpoint to retrieve comprehensive portfolio statistics.
    
    Provides key metrics and analytics about the portfolio including:
    - Total number of projects and their status breakdown
    - Featured projects count for homepage highlights
    - Skills count and category distribution
    - Years of experience calculation
    - Performance monitoring for analytics queries
    
    This endpoint is ideal for dashboard displays, portfolio summaries,
    and analytics sections that showcase portfolio scope and expertise.
    
    Returns:
        Response: JSON object containing portfolio statistics and metrics
    """
    with PerformanceMonitor('portfolio_stats_query'):
        total_projects = Project.objects.count()
        completed_projects = Project.objects.filter(status='completed').count()
        featured_projects = Project.objects.filter(featured=True).count()
        
        total_skills = Skill.objects.count()
        skill_categories = Skill.objects.values_list('category', flat=True).distinct().count()
        
        # Calculate years of experience (you might want to adjust this logic)
        years_experience = 5  # This could be calculated based on earliest project date
        
        return Response({
            'total_projects': total_projects,
            'completed_projects': completed_projects,
            'featured_projects': featured_projects,
            'total_skills': total_skills,
            'skill_categories': skill_categories,
            'years_experience': years_experience
        })
