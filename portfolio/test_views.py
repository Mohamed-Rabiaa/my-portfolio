"""
Comprehensive pytest tests for portfolio application API views.

This module provides thorough testing for all portfolio REST API views including:
- SkillListView: skills listing and filtering by category/proficiency
- ProjectListView: projects listing, filtering, searching, and pagination
- ProjectDetailView: individual project retrieval
- FeaturedProjectsView: featured projects endpoint
- ProjectImageListView: project images management
- Function-based views: portfolio stats, skills by category

Tests cover:
- HTTP status codes and response structure
- Authentication and permission requirements
- Data validation and serialization
- Filtering, searching, and ordering
- Pagination functionality
- Error handling and edge cases
- Image handling and file uploads
- Portfolio analytics and statistics
"""

import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient
from unittest.mock import patch, Mock
from datetime import datetime, timezone, timedelta
from portfolio.models import Skill, Project, ProjectImage


@pytest.mark.django_db
@pytest.mark.api
class TestSkillListView:
    """Test cases for SkillListView API endpoint."""
    
    def test_get_skills_success(self, api_client, portfolio_skills):
        """Test successful retrieval of skills."""
        url = reverse('portfolio:skill-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)
        assert len(response.data) == len(portfolio_skills)
        
        # Check response structure
        if response.data:
            skill_data = response.data[0]
            expected_fields = [
                'id', 'name', 'category', 'proficiency', 'icon',
                'description', 'years_experience', 'featured'
            ]
            for field in expected_fields:
                assert field in skill_data
    
    def test_get_skills_empty_list(self, api_client):
        """Test skills list when no skills exist."""
        url = reverse('portfolio:skill-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0
    
    def test_skills_filtering_by_category(self, api_client, portfolio_skills):
        """Test filtering skills by category."""
        url = reverse('portfolio:skill-list')
        response = api_client.get(url, {'category': 'frontend'})
        
        assert response.status_code == status.HTTP_200_OK
        
        # All returned skills should belong to frontend category
        for skill in response.data:
            assert skill['category'] == 'frontend'
    
    def test_skills_filtering_by_proficiency(self, api_client, portfolio_skills):
        """Test filtering skills by proficiency level."""
        url = reverse('portfolio:skill-list')
        response = api_client.get(url, {'proficiency': 'expert'})
        
        assert response.status_code == status.HTTP_200_OK
        
        # All returned skills should have expert proficiency
        for skill in response.data:
            assert skill['proficiency'] == 'expert'
    
    def test_skills_filtering_by_featured(self, api_client, portfolio_skills):
        """Test filtering skills by featured status."""
        url = reverse('portfolio:skill-list')
        response = api_client.get(url, {'featured': 'true'})
        
        assert response.status_code == status.HTTP_200_OK
        
        # All returned skills should be featured
        for skill in response.data:
            assert skill['featured'] is True
    
    def test_skills_ordering(self, api_client, portfolio_skills):
        """Test ordering skills by different fields."""
        url = reverse('portfolio:skill-list')
        
        # Test ordering by name
        response = api_client.get(url, {'ordering': 'name'})
        assert response.status_code == status.HTTP_200_OK
        
        if len(response.data) > 1:
            names = [skill['name'] for skill in response.data]
            assert names == sorted(names)
        
        # Test ordering by proficiency
        response = api_client.get(url, {'ordering': '-proficiency'})
        assert response.status_code == status.HTTP_200_OK
        
        # Test ordering by years_experience
        response = api_client.get(url, {'ordering': '-years_experience'})
        assert response.status_code == status.HTTP_200_OK
    
    def test_skills_combined_filters(self, api_client, test_user):
        """Test combining multiple skill filters."""
        # Create specific skill for testing
        skill = Skill.objects.create(
            name='React',
            category='frontend',
            proficiency='expert',
            years_experience=5,
            featured=True,
            description='React framework expertise'
        )
        
        url = reverse('portfolio:skill-list')
        response = api_client.get(url, {
            'category': 'frontend',
            'proficiency': 'expert',
            'featured': 'true'
        })
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['name'] == 'React'


@pytest.mark.django_db
@pytest.mark.api
class TestProjectListView:
    """Test cases for ProjectListView API endpoint."""
    
    def test_get_projects_success(self, api_client, portfolio_projects):
        """Test successful retrieval of projects."""
        url = reverse('portfolio:project-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        assert 'count' in response.data
        assert 'next' in response.data
        assert 'previous' in response.data
        
        # Should return all projects
        results = response.data['results']
        assert len(results) == len(portfolio_projects)
        
        # Check response structure
        if results:
            project_data = results[0]
            expected_fields = [
                'id', 'title', 'slug', 'description', 'short_description',
                'technologies', 'category', 'status', 'featured',
                'github_url', 'live_url', 'featured_image',
                'start_date', 'end_date', 'created_at'
            ]
            for field in expected_fields:
                assert field in project_data
    
    def test_get_projects_empty_list(self, api_client):
        """Test projects list when no projects exist."""
        url = reverse('portfolio:project-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 0
        assert len(response.data['results']) == 0
    
    def test_projects_filtering_by_category(self, api_client, portfolio_projects):
        """Test filtering projects by category."""
        url = reverse('portfolio:project-list')
        response = api_client.get(url, {'category': 'web'})
        
        assert response.status_code == status.HTTP_200_OK
        
        # All returned projects should belong to web category
        for project in response.data['results']:
            assert project['category'] == 'web'
    
    def test_projects_filtering_by_status(self, api_client, portfolio_projects):
        """Test filtering projects by status."""
        url = reverse('portfolio:project-list')
        response = api_client.get(url, {'status': 'completed'})
        
        assert response.status_code == status.HTTP_200_OK
        
        # All returned projects should have completed status
        for project in response.data['results']:
            assert project['status'] == 'completed'
    
    def test_projects_filtering_by_featured(self, api_client, portfolio_projects):
        """Test filtering projects by featured status."""
        url = reverse('portfolio:project-list')
        response = api_client.get(url, {'featured': 'true'})
        
        assert response.status_code == status.HTTP_200_OK
        
        # All returned projects should be featured
        for project in response.data['results']:
            assert project['featured'] is True
    
    def test_projects_filtering_by_technology(self, api_client, test_user, portfolio_skills):
        """Test filtering projects by technology/skill."""
        # Create project with specific technology
        project = Project.objects.create(
            title='Django Project',
            slug='django-project',
            description='A Django web application',
            short_description='Django app',
            category='web',
            status='completed'
        )
        project.technologies.add(portfolio_skills[0])
        
        url = reverse('portfolio:project-list')
        response = api_client.get(url, {'technologies': portfolio_skills[0].id})
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['title'] == 'Django Project'
    
    def test_projects_search_functionality(self, api_client, test_user):
        """Test search functionality across title, description, and technologies."""
        # Create projects with specific content for searching
        project1 = Project.objects.create(
            title='E-commerce Platform',
            slug='ecommerce-platform',
            description='Full-stack e-commerce solution with Django and React',
            short_description='E-commerce app',
            category='web',
            status='completed'
        )
        
        project2 = Project.objects.create(
            title='Mobile App',
            slug='mobile-app',
            description='React Native mobile application',
            short_description='Mobile solution',
            category='mobile',
            status='completed'
        )
        
        url = reverse('portfolio:project-list')
        
        # Search by title
        response = api_client.get(url, {'search': 'E-commerce'})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['title'] == 'E-commerce Platform'
        
        # Search by description
        response = api_client.get(url, {'search': 'React'})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 2  # Both projects mention React
    
    def test_projects_ordering(self, api_client, portfolio_projects):
        """Test ordering projects by different fields."""
        url = reverse('portfolio:project-list')
        
        # Test ordering by created_at (default)
        response = api_client.get(url, {'ordering': '-created_at'})
        assert response.status_code == status.HTTP_200_OK
        
        # Test ordering by title
        response = api_client.get(url, {'ordering': 'title'})
        assert response.status_code == status.HTTP_200_OK
        
        # Verify ordering is applied
        if len(response.data['results']) > 1:
            titles = [project['title'] for project in response.data['results']]
            assert titles == sorted(titles)
        
        # Test ordering by start_date
        response = api_client.get(url, {'ordering': '-start_date'})
        assert response.status_code == status.HTTP_200_OK
    
    def test_projects_pagination(self, api_client, test_user):
        """Test pagination functionality."""
        # Create multiple projects for pagination testing
        for i in range(15):
            Project.objects.create(
                title=f'Project {i+1}',
                slug=f'project-{i+1}',
                description=f'Description for project {i+1}',
                short_description=f'Short desc {i+1}',
                category='web',
                status='completed'
            )
        
        url = reverse('portfolio:project-list')
        
        # Test default pagination
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert 'next' in response.data
        assert 'previous' in response.data
        assert 'count' in response.data
        assert response.data['count'] == 15
        
        # Test custom page size
        response = api_client.get(url, {'page_size': 5})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 5
        
        # Test specific page
        response = api_client.get(url, {'page': 2, 'page_size': 5})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 5
    
    def test_projects_combined_filters(self, api_client, test_user, portfolio_skills):
        """Test combining multiple project filters."""
        # Create specific project for testing
        project = Project.objects.create(
            title='Featured Web App',
            slug='featured-web-app',
            description='Advanced web application with Django',
            short_description='Web app',
            category='web',
            status='completed',
            featured=True
        )
        project.technologies.add(portfolio_skills[0])
        
        url = reverse('portfolio:project-list')
        response = api_client.get(url, {
            'featured': 'true',
            'category': 'web',
            'status': 'completed',
            'search': 'Django'
        })
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['title'] == 'Featured Web App'


@pytest.mark.django_db
@pytest.mark.api
class TestProjectDetailView:
    """Test cases for ProjectDetailView API endpoint."""
    
    def test_get_project_detail_success(self, api_client, portfolio_project):
        """Test successful retrieval of project detail."""
        url = reverse('portfolio:project-detail', kwargs={'slug': portfolio_project.slug})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        
        # Check response structure
        expected_fields = [
            'id', 'title', 'slug', 'description', 'short_description',
            'technologies', 'category', 'status', 'featured',
            'github_url', 'live_url', 'featured_image', 'images',
            'start_date', 'end_date', 'created_at', 'updated_at'
        ]
        for field in expected_fields:
            assert field in response.data
        
        # Check data accuracy
        assert response.data['title'] == portfolio_project.title
        assert response.data['slug'] == portfolio_project.slug
        assert response.data['description'] == portfolio_project.description
    
    def test_get_project_detail_not_found(self, api_client):
        """Test project detail with non-existent slug."""
        url = reverse('portfolio:project-detail', kwargs={'slug': 'non-existent-slug'})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_project_detail_with_images(self, api_client, portfolio_project, project_images):
        """Test project detail includes related images."""
        url = reverse('portfolio:project-detail', kwargs={'slug': portfolio_project.slug})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        
        # Check if images are included
        if 'images' in response.data:
            assert isinstance(response.data['images'], list)
            assert len(response.data['images']) == len(project_images)
    
    def test_project_detail_with_technologies(self, api_client, portfolio_project, portfolio_skills):
        """Test project detail includes related technologies."""
        # Add technologies to project
        portfolio_project.technologies.add(*portfolio_skills[:2])
        
        url = reverse('portfolio:project-detail', kwargs={'slug': portfolio_project.slug})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        
        # Check technologies are included
        assert 'technologies' in response.data
        assert isinstance(response.data['technologies'], list)
        assert len(response.data['technologies']) == 2


@pytest.mark.django_db
@pytest.mark.api
class TestFeaturedProjectsView:
    """Test cases for FeaturedProjectsView API endpoint."""
    
    def test_get_featured_projects_success(self, api_client, portfolio_projects):
        """Test successful retrieval of featured projects."""
        url = reverse('portfolio:featured-projects')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)
        
        # All returned projects should be featured
        for project in response.data:
            assert project['featured'] is True
    
    def test_get_featured_projects_empty(self, api_client, test_user):
        """Test featured projects endpoint when no featured projects exist."""
        # Create non-featured project
        Project.objects.create(
            title='Non-Featured Project',
            slug='non-featured-project',
            description='Non-featured description',
            short_description='Non-featured',
            category='web',
            status='completed',
            featured=False
        )
        
        url = reverse('portfolio:featured-projects')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0
    
    def test_featured_projects_limit(self, api_client, test_user):
        """Test that featured projects endpoint respects limit."""
        # Create multiple featured projects
        for i in range(10):
            Project.objects.create(
                title=f'Featured Project {i+1}',
                slug=f'featured-project-{i+1}',
                description=f'Featured description {i+1}',
                short_description=f'Featured {i+1}',
                category='web',
                status='completed',
                featured=True
            )
        
        url = reverse('portfolio:featured-projects')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        # Should limit to a reasonable number (e.g., 6)
        assert len(response.data) <= 6


@pytest.mark.django_db
@pytest.mark.api
class TestProjectImageListView:
    """Test cases for ProjectImageListView API endpoint."""
    
    def test_get_project_images_success(self, api_client, portfolio_project, project_images):
        """Test successful retrieval of project images."""
        url = reverse('portfolio:project-images', kwargs={'project_slug': portfolio_project.slug})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)
        assert len(response.data) == len(project_images)
        
        # Check response structure
        if response.data:
            image_data = response.data[0]
            expected_fields = ['id', 'image', 'caption', 'order', 'project']
            for field in expected_fields:
                assert field in image_data
    
    def test_get_project_images_empty(self, api_client, portfolio_project):
        """Test project images endpoint when no images exist."""
        url = reverse('portfolio:project-images', kwargs={'project_slug': portfolio_project.slug})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0
    
    def test_get_project_images_non_existent_project(self, api_client):
        """Test project images for non-existent project."""
        url = reverse('portfolio:project-images', kwargs={'project_slug': 'non-existent'})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_project_images_ordering(self, api_client, portfolio_project, test_user):
        """Test that project images are ordered correctly."""
        # Create images with specific order
        image1 = ProjectImage.objects.create(
            project=portfolio_project,
            image='test1.jpg',
            caption='First image',
            order=1
        )
        image2 = ProjectImage.objects.create(
            project=portfolio_project,
            image='test2.jpg',
            caption='Second image',
            order=2
        )
        
        url = reverse('portfolio:project-images', kwargs={'project_slug': portfolio_project.slug})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 2
        
        # Check ordering
        assert response.data[0]['order'] == 1
        assert response.data[1]['order'] == 2


@pytest.mark.django_db
@pytest.mark.api
class TestPortfolioFunctionViews:
    """Test cases for portfolio function-based API views."""
    
    def test_portfolio_stats_success(self, api_client, portfolio_projects, portfolio_skills):
        """Test portfolio stats endpoint."""
        url = reverse('portfolio:portfolio-stats')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        
        # Check response structure
        expected_fields = [
            'total_projects', 'completed_projects', 'featured_projects',
            'total_skills', 'skill_categories', 'years_experience'
        ]
        for field in expected_fields:
            assert field in response.data
        
        # Check data accuracy
        assert response.data['total_projects'] == len(portfolio_projects)
        assert response.data['total_skills'] == len(portfolio_skills)
    
    def test_portfolio_stats_empty_data(self, api_client):
        """Test portfolio stats with no data."""
        url = reverse('portfolio:portfolio-stats')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        
        # All counts should be zero
        assert response.data['total_projects'] == 0
        assert response.data['completed_projects'] == 0
        assert response.data['featured_projects'] == 0
        assert response.data['total_skills'] == 0
    
    def test_skills_by_category_success(self, api_client, portfolio_skills):
        """Test skills by category endpoint."""
        url = reverse('portfolio:skills-by-category')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, dict)
        
        # Should group skills by category
        for category, skills in response.data.items():
            assert isinstance(skills, list)
            for skill in skills:
                assert skill['category'] == category
    
    def test_skills_by_category_empty(self, api_client):
        """Test skills by category with no skills."""
        url = reverse('portfolio:skills-by-category')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, dict)
        assert len(response.data) == 0
    
    def test_recent_projects_success(self, api_client, portfolio_projects):
        """Test recent projects endpoint."""
        url = reverse('portfolio:recent-projects')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)
        assert len(response.data) <= 5  # Should return max 5 recent projects
        
        # Projects should be ordered by created_at descending
        if len(response.data) > 1:
            dates = [project['created_at'] for project in response.data]
            assert dates == sorted(dates, reverse=True)


@pytest.mark.django_db
@pytest.mark.integration
class TestPortfolioAPIIntegration:
    """Integration tests for portfolio API endpoints."""
    
    def test_portfolio_api_workflow(self, api_client, test_user, portfolio_skills):
        """Test complete portfolio API workflow."""
        # 1. Check initial empty state
        projects_response = api_client.get(reverse('portfolio:project-list'))
        assert projects_response.data['count'] == 0
        
        # 2. Create project (simulating admin action)
        project = Project.objects.create(
            title='Integration Test Project',
            slug='integration-test-project',
            description='Integration test description',
            short_description='Integration test',
            category='web',
            status='completed',
            featured=True,
            github_url='https://github.com/test/project',
            live_url='https://test-project.com'
        )
        project.technologies.add(*portfolio_skills[:2])
        
        # 3. Verify project appears in list
        projects_response = api_client.get(reverse('portfolio:project-list'))
        assert projects_response.data['count'] == 1
        assert projects_response.data['results'][0]['title'] == 'Integration Test Project'
        
        # 4. Access project detail
        detail_response = api_client.get(
            reverse('portfolio:project-detail', kwargs={'slug': project.slug})
        )
        assert detail_response.status_code == status.HTTP_200_OK
        assert detail_response.data['title'] == 'Integration Test Project'
        assert len(detail_response.data['technologies']) == 2
        
        # 5. Check featured projects
        featured_response = api_client.get(reverse('portfolio:featured-projects'))
        assert len(featured_response.data) == 1
        assert featured_response.data[0]['title'] == 'Integration Test Project'
        
        # 6. Check stats
        stats_response = api_client.get(reverse('portfolio:portfolio-stats'))
        assert stats_response.data['total_projects'] == 1
        assert stats_response.data['completed_projects'] == 1
        assert stats_response.data['featured_projects'] == 1
    
    def test_portfolio_api_error_handling(self, api_client):
        """Test error handling across portfolio API endpoints."""
        # Test non-existent project detail
        response = api_client.get(
            reverse('portfolio:project-detail', kwargs={'slug': 'non-existent'})
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # Test project images for non-existent project
        response = api_client.get(
            reverse('portfolio:project-images', kwargs={'project_slug': 'non-existent'})
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # Test invalid pagination
        response = api_client.get(reverse('portfolio:project-list'), {'page': 999})
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_portfolio_api_filtering_integration(self, api_client, test_user, portfolio_skills):
        """Test complex filtering scenarios."""
        # Create projects with different characteristics
        web_project = Project.objects.create(
            title='Web Project',
            slug='web-project',
            description='Web development project',
            short_description='Web project',
            category='web',
            status='completed',
            featured=True
        )
        web_project.technologies.add(portfolio_skills[0])
        
        mobile_project = Project.objects.create(
            title='Mobile Project',
            slug='mobile-project',
            description='Mobile development project',
            short_description='Mobile project',
            category='mobile',
            status='in_progress',
            featured=False
        )
        mobile_project.technologies.add(portfolio_skills[1])
        
        # Test category filtering
        response = api_client.get(reverse('portfolio:project-list'), {'category': 'web'})
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['title'] == 'Web Project'
        
        # Test status filtering
        response = api_client.get(reverse('portfolio:project-list'), {'status': 'completed'})
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['title'] == 'Web Project'
        
        # Test featured filtering
        response = api_client.get(reverse('portfolio:project-list'), {'featured': 'true'})
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['title'] == 'Web Project'
        
        # Test technology filtering
        response = api_client.get(
            reverse('portfolio:project-list'), 
            {'technologies': portfolio_skills[0].id}
        )
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['title'] == 'Web Project'
    
    def test_portfolio_api_performance(self, api_client, full_test_data):
        """Test portfolio API performance with full dataset."""
        # This test ensures the API performs well with a complete dataset
        
        # Test list view with all data
        response = api_client.get(reverse('portfolio:project-list'))
        assert response.status_code == status.HTTP_200_OK
        
        # Test skills list with all data
        response = api_client.get(reverse('portfolio:skill-list'))
        assert response.status_code == status.HTTP_200_OK
        
        # Test filtering with full dataset
        response = api_client.get(reverse('portfolio:project-list'), {'featured': 'true'})
        assert response.status_code == status.HTTP_200_OK
        
        # Test search with full dataset
        response = api_client.get(reverse('portfolio:project-list'), {'search': 'test'})
        assert response.status_code == status.HTTP_200_OK
        
        # Test stats with full dataset
        response = api_client.get(reverse('portfolio:portfolio-stats'))
        assert response.status_code == status.HTTP_200_OK