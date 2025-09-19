from rest_framework import generics, filters
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from .models import Project, Skill
from .serializers import ProjectSerializer, ProjectListSerializer, SkillSerializer


class ProjectListView(generics.ListAPIView):
    """List all projects with filtering and search"""
    queryset = Project.objects.all()
    serializer_class = ProjectListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['featured', 'technologies__category']
    search_fields = ['title', 'description', 'technologies__name']
    ordering_fields = ['created_at', 'title']
    ordering = ['-featured', '-created_at']


class ProjectDetailView(generics.RetrieveAPIView):
    """Retrieve a single project by slug"""
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer
    lookup_field = 'slug'


class FeaturedProjectsView(generics.ListAPIView):
    """List featured projects only"""
    queryset = Project.objects.filter(featured=True)
    serializer_class = ProjectListSerializer


class SkillListView(generics.ListAPIView):
    """List all skills grouped by category"""
    queryset = Skill.objects.all()
    serializer_class = SkillSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['category', 'proficiency']
    ordering = ['category', 'name']


@api_view(['GET'])
def skills_by_category(request):
    """Get skills grouped by category"""
    categories = ['frontend', 'backend', 'database', 'tools']
    result = {}
    
    for category in categories:
        skills = Skill.objects.filter(category=category)
        result[category] = SkillSerializer(skills, many=True).data
    
    return Response(result)


@api_view(['GET'])
def portfolio_stats(request):
    """Get portfolio statistics"""
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
