from django.urls import path
from . import views

app_name = 'portfolio'

urlpatterns = [
    # Project endpoints
    path('projects/', views.ProjectListView.as_view(), name='project-list'),
    path('projects/<slug:slug>/', views.ProjectDetailView.as_view(), name='project-detail'),
    path('projects/featured/', views.FeaturedProjectsView.as_view(), name='featured-projects'),
    
    # Skill endpoints
    path('skills/', views.SkillListView.as_view(), name='skill-list'),
    path('skills/by-category/', views.skills_by_category, name='skills-by-category'),
    
    # Statistics
    path('stats/', views.portfolio_stats, name='portfolio-stats'),
]