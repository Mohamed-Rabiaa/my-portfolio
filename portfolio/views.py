"""
Portfolio application views for showcasing projects and skills.

This module provides REST API views for the portfolio functionality including:
- Project listing, detail viewing, and filtering
- Skill management and categorization
- Featured project highlights
- Portfolio statistics and analytics
- Skills organized by category for better presentation
"""

from rest_framework import generics, filters
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Project, Skill
from .serializers import ProjectSerializer, ProjectListSerializer, SkillSerializer


class ProjectListView(generics.ListAPIView):
    """
    API view to list all portfolio projects with advanced filtering capabilities.
    
    Provides comprehensive project listing with support for:
    - Filtering by featured status and technology categories
    - Full-text search across project titles, descriptions, and technologies
    - Ordering by creation date or title
    - Featured projects displayed first for prominence
    
    This view is ideal for portfolio galleries, project archives, and
    filtered project displays based on specific technologies or criteria.
    """
    queryset = Project.objects.all()
    serializer_class = ProjectListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['featured', 'technologies__category']
    search_fields = ['title', 'description', 'technologies__name']
    ordering_fields = ['created_at', 'title']
    ordering = ['-featured', '-created_at']


class ProjectDetailView(generics.RetrieveAPIView):
    """
    API view to retrieve a single project by its slug.
    
    Provides detailed project information including:
    - Complete project description and details
    - Associated technologies and skills
    - Project links (GitHub, live demo)
    - Project images and gallery
    - All metadata and timestamps
    
    Uses slug-based lookup for SEO-friendly URLs and better user experience.
    """
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    lookup_field = 'slug'


class FeaturedProjectsView(generics.ListAPIView):
    """
    API view to list only featured portfolio projects.
    
    Returns a curated list of projects marked as 'featured' by administrators.
    This endpoint is commonly used for:
    - Homepage project highlights
    - Portfolio showcase sections
    - "Best Work" displays
    - Landing page content
    
    Projects maintain their natural ordering (featured first, then by date).
    """
    queryset = Project.objects.filter(featured=True)
    serializer_class = ProjectListSerializer


class SkillListView(generics.ListAPIView):
    """
    API view to list all technical skills with filtering capabilities.
    
    Provides comprehensive skill listing with support for:
    - Filtering by skill category (frontend, backend, database, tools)
    - Filtering by proficiency level (beginner to expert)
    - Ordering by category and name for organized display
    
    This view supports skill showcase sections, technology filters,
    and competency displays across the portfolio.
    """
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['category', 'proficiency']
    ordering = ['category', 'name']


@api_view(['GET'])
def skills_by_category(request):
    """
    API endpoint to retrieve skills organized by category.
    
    Returns skills grouped into predefined categories for structured display:
    - frontend: Frontend development technologies
    - backend: Backend development technologies
    - database: Database and data storage technologies
    - tools: Development tools and other technologies
    
    This endpoint is ideal for creating organized skill sections,
    technology showcases, and categorized competency displays.
    
    Args:
        request: HTTP GET request object
        
    Returns:
        Response: JSON object with skills grouped by category, where each
                 category contains an array of skill objects with full details
    """
    categories = ['frontend', 'backend', 'database', 'tools']
    result = {}
    
    for category in categories:
        skills = Skill.objects.filter(category=category)
        result[category] = SkillSerializer(skills, many=True).data
    
    return Response(result)


@api_view(['GET'])
def portfolio_stats(request):
    """
    API endpoint to retrieve comprehensive portfolio statistics.
    
    Provides key metrics about the portfolio content including:
    - Total number of projects
    - Number of featured projects
    - Total number of skills
    - Skills breakdown by category
    
    This endpoint is useful for:
    - Dashboard displays and analytics
    - Portfolio overview widgets
    - Statistics sections on the website
    - Administrative insights
    
    Args:
        request: HTTP GET request object
        
    Returns:
        Response: JSON object containing portfolio statistics with keys:
            - total_projects: Total number of projects
            - featured_projects: Number of featured projects
            - total_skills: Total number of skills
            - skills_by_category: Object with skill counts per category
    """
    stats = {
        'total_projects': Project.objects.count(),
        'featured_projects': Project.objects.filter(featured=True).count(),
        'total_skills': Skill.objects.count(),
        'skills_by_category': {
            'frontend': Skill.objects.filter(category='frontend').count(),
            'backend': Skill.objects.filter(category='backend').count(),
            'database': Skill.objects.filter(category='database').count(),
            'tools': Skill.objects.filter(category='tools').count(),
        }
    }
    return Response(stats)
