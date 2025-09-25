from django.urls import path
from . import views
from .profile_views import admin_profile, AdminProfileDetailView, UserProfileDetailView

app_name = 'portfolio'

urlpatterns = [
    # Project endpoints
    path('projects/', views.ProjectListView.as_view(), name='project-list'),
    path('projects/<slug:slug>/', views.ProjectDetailView.as_view(), name='project-detail'),
    path('projects/featured/', views.FeaturedProjectsView.as_view(), name='featured-projects'),
    
    # Skill endpoints
    path('skills/', views.SkillListView.as_view(), name='skill-list'),
    path('skills/by-category/', views.skills_by_category, name='skills-by-category'),
    
    # Profile endpoints
    path('admin-profile/', admin_profile, name='admin-profile'),
    path('admin-profile-detail/', AdminProfileDetailView.as_view(), name='admin-profile-detail'),
    path('profile/', UserProfileDetailView.as_view(), name='user-profile'),
    
    # Statistics
    path('stats/', views.portfolio_stats, name='portfolio-stats'),
]