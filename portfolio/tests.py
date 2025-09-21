"""
Comprehensive pytest unit tests for portfolio app API views.

This module contains test cases for all portfolio API endpoints including:
- Project listing and filtering
- Skill listing and categorization
- Portfolio statistics
- Skills by category endpoint

Test Coverage:
- All API views and endpoints
- Response status codes and data structure
- Filtering and search functionality
- Error handling and edge cases
- Authentication requirements (if any)
"""

import pytest
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from unittest.mock import patch
from portfolio.models import Project, Skill, ProjectImage
from portfolio.views import ProjectListView, SkillListView


@pytest.mark.django_db
class TestProjectListView(APITestCase):
    """Test cases for ProjectListView API endpoint."""
    
    def setUp(self):
        """Set up test data for project tests."""
        self.client = APIClient()
        self.url = reverse('portfolio:project-list')
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test skills (technologies)
        self.skill1 = Skill.objects.create(name='Python', category='backend', proficiency=4)
        self.skill2 = Skill.objects.create(name='React', category='frontend', proficiency=3)
        
        # Create test projects
        self.project1 = Project.objects.create(
            title='Test Project 1',
            description='First test project',
            featured=True
        )
        self.project1.technologies.add(self.skill1)
        
        self.project2 = Project.objects.create(
            title='Test Project 2',
            description='Second test project',
            featured=False
        )
        self.project2.technologies.add(self.skill2)
        
        self.project3 = Project.objects.create(
            title='Another Project',
            description='Third test project',
            featured=False
        )
    
    def test_get_project_list_success(self):
        """Test successful retrieval of project list."""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, dict)
        self.assertIn('results', response.data)
        
        # Should return all projects
        results = response.data['results']
        self.assertEqual(len(results), 3)
        
        # Check project data structure
        project_data = response.data['results'][0]
        expected_fields = ['id', 'title', 'slug', 'description', 'technologies', 'github_url', 'live_url', 'image', 'featured', 'created_at']
        for field in expected_fields:
            self.assertIn(field, project_data)
    
    def test_project_list_filtering_by_featured(self):
        """Test filtering projects by featured status."""
        response = self.client.get(self.url, {'featured': 'true'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'Test Project 1')
        self.assertTrue(results[0]['featured'])
    
    def test_project_list_filtering_by_technologies(self):
        """Test filtering projects by technology category."""
        response = self.client.get(self.url, {'technologies__category': 'backend'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        
        # Check that the returned project has the correct technology
        project = response.data['results'][0]
        self.assertEqual(project['title'], 'Test Project 1')
    
    def test_project_list_search_functionality(self):
        """Test search functionality in project list."""
        response = self.client.get(self.url, {'search': 'Test Project 1'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['title'], 'Test Project 1')
    
    def test_project_list_ordering(self):
        """Test ordering of project list."""
        response = self.client.get(self.url, {'ordering': '-created_at'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that projects are ordered by creation date (newest first)
        projects = response.data['results']
        self.assertEqual(len(projects), 3)
        
        # Verify ordering (newest first)
        for i in range(len(projects) - 1):
            current_date = projects[i]['created_at']
            next_date = projects[i + 1]['created_at']
            self.assertGreaterEqual(current_date, next_date)
    
    def test_project_list_reverse_ordering(self):
        """Test reverse ordering functionality."""
        response = self.client.get(self.url, {'ordering': '-title'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        self.assertEqual(len(results), 3)
        self.assertEqual(results[0]['title'], 'Test Project 2')
        self.assertEqual(results[1]['title'], 'Test Project 1')
        self.assertEqual(results[2]['title'], 'Another Project')
    
    def test_project_list_empty_results(self):
        """Test handling of empty results."""
        # Delete all projects
        Project.objects.all().delete()
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)


@pytest.mark.django_db
class TestSkillListView(APITestCase):
    """Test cases for SkillListView API endpoint."""
    
    def setUp(self):
        """Set up test data for skill tests."""
        self.client = APIClient()
        self.url = reverse('portfolio:skill-list')
        
        # Create test skills with correct categories from models
        self.skill1 = Skill.objects.create(
            name='Python',
            category='backend',
            proficiency=4
        )
        
        self.skill2 = Skill.objects.create(
            name='Django',
            category='backend',
            proficiency=3
        )
        
        self.skill3 = Skill.objects.create(
            name='JavaScript',
            category='frontend',
            proficiency=3
        )
    
    def test_get_skill_list_success(self):
        """Test successful retrieval of skill list."""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, dict)
        self.assertIn('results', response.data)
        self.assertEqual(len(response.data['results']), 3)
        
        # Check skill data structure
        skill_data = response.data['results'][0]
        expected_fields = ['id', 'name', 'category', 'category_display', 'proficiency', 'proficiency_display', 'created_at']
        for field in expected_fields:
            self.assertIn(field, skill_data)
    
    def test_skill_list_filter_by_category(self):
        """Test filtering skills by category."""
        response = self.client.get(self.url, {'category': 'backend'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 2)  # Python and Django are backend       
        for skill in response.data['results']:
            self.assertEqual(skill['category'], 'backend')
    
    def test_skill_list_search_functionality(self):
        """Test search functionality for skills."""
        response = self.client.get(self.url, {'search': 'Python'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # The search might match multiple skills, so let's check that Python is in the results
        results = response.data['results']
        python_skills = [skill for skill in results if 'Python' in skill['name']]
        self.assertGreater(len(python_skills), 0)
        self.assertEqual(python_skills[0]['name'], 'Python')
    
    def test_skill_list_ordering_by_proficiency(self):
        """Test ordering skills by proficiency."""
        response = self.client.get(self.url, {'ordering': '-proficiency'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 3)
        
        # Should be ordered by proficiency descending
        proficiencies = [skill['proficiency'] for skill in response.data['results']]
        self.assertEqual(proficiencies, [4, 3, 3])
    
    def test_skill_list_empty_results(self):
        """Test handling of empty skill results."""
        Skill.objects.all().delete()
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)


@pytest.mark.django_db
class TestSkillsByCategoryView(APITestCase):
    """Test cases for skills_by_category function-based view."""
    
    def setUp(self):
        """Set up test data for skills by category tests."""
        self.client = APIClient()
        self.url = reverse('portfolio:skills-by-category')
        
        # Create test skills in different categories
        self.skill1 = Skill.objects.create(
            name='Python',
            category='backend',
            proficiency=4
        )
        
        self.skill2 = Skill.objects.create(
            name='JavaScript',
            category='frontend',
            proficiency=3
        )
        
        self.skill3 = Skill.objects.create(
            name='PostgreSQL',
            category='database',
            proficiency=3
        )
        
        self.skill4 = Skill.objects.create(
            name='Git',
            category='tools',
            proficiency=4
        )
    
    def test_skills_by_category_success(self):
        """Test successful retrieval of skills grouped by category."""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, dict)
        
        # Check that all categories are present
        expected_categories = ['frontend', 'backend', 'database', 'tools']
        for category in expected_categories:
            self.assertIn(category, response.data)
        
        # Check specific skills in their categories
        self.assertEqual(len(response.data['backend']), 1)
        self.assertEqual(response.data['backend'][0]['name'], 'Python')
        
        self.assertEqual(len(response.data['frontend']), 1)
        self.assertEqual(response.data['frontend'][0]['name'], 'JavaScript')
        
        self.assertEqual(len(response.data['database']), 1)
        self.assertEqual(response.data['database'][0]['name'], 'PostgreSQL')
        
        self.assertEqual(len(response.data['tools']), 1)
        self.assertEqual(response.data['tools'][0]['name'], 'Git')
    
    def test_skills_by_category_structure(self):
        """Test the structure of skills by category response."""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check skill data structure within categories
        for category, skills in response.data.items():
            self.assertIsInstance(skills, list)
            for skill in skills:
                expected_fields = ['id', 'name', 'category', 'proficiency']
                for field in expected_fields:
                    self.assertIn(field, skill)
    
    def test_skills_by_category_empty_results(self):
        """Test handling when no skills exist."""
        # Delete all skills
        Skill.objects.all().delete()
        
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should return empty arrays for each category, not empty dict
        expected_categories = ['frontend', 'backend', 'database', 'tools']
        for category in expected_categories:
            self.assertIn(category, response.data)
            self.assertEqual(response.data[category], [])


@pytest.mark.django_db
class TestPortfolioStatsView(APITestCase):
    """Test cases for portfolio_stats function-based view."""
    
    def setUp(self):
        """Set up test data for portfolio stats tests."""
        self.client = APIClient()
        self.url = reverse('portfolio:portfolio-stats')
        
        # Create test data
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create skills
        self.skill1 = Skill.objects.create(
            name='Python',
            category='backend',
            proficiency=4
        )
        self.skill2 = Skill.objects.create(
            name='React',
            category='frontend',
            proficiency=3
        )
        
        # Create projects
        self.project1 = Project.objects.create(
            title='Project 1',
            description='Test project 1',
            featured=True
        )
        
        self.project2 = Project.objects.create(
            title='Project 2',
            description='Test project 2',
            featured=False
        )
    
    def test_portfolio_stats_success(self):
        """Test successful retrieval of portfolio statistics."""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, dict)
        
        # Check expected statistics fields
        expected_fields = [
            'total_projects',
            'featured_projects',
            'total_skills',
            'skills_by_category'
        ]
        
        for field in expected_fields:
            self.assertIn(field, response.data)
    
    def test_portfolio_stats_values(self):
        """Test the accuracy of portfolio statistics values."""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify statistics values
        self.assertEqual(response.data['total_projects'], 2)
        self.assertEqual(response.data['featured_projects'], 1)
        self.assertEqual(response.data['total_skills'], 2)
        
        # Check skills by category structure
        skills_by_category = response.data['skills_by_category']
        expected_categories = ['frontend', 'backend', 'database', 'tools']
        for category in expected_categories:
            self.assertIn(category, skills_by_category)
        
        # Check specific counts
        self.assertEqual(skills_by_category['backend'], 1)  # Python
        self.assertEqual(skills_by_category['frontend'], 1)  # React
    
    def test_portfolio_stats_empty_data(self):
        """Test portfolio stats with no data."""
        # Delete all test data
        Project.objects.all().delete()
        Skill.objects.all().delete()
        
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # All counts should be zero
        self.assertEqual(response.data['total_projects'], 0)
        self.assertEqual(response.data['featured_projects'], 0)
        self.assertEqual(response.data['total_skills'], 0)
        
        # Skills by category should be empty
        skills_by_category = response.data['skills_by_category']
        expected_categories = ['frontend', 'backend', 'database', 'tools']
        for category in expected_categories:
            self.assertEqual(skills_by_category[category], 0)


@pytest.mark.django_db
class TestPortfolioAPIIntegration(APITestCase):
    """Integration tests for portfolio API endpoints."""
    
    def setUp(self):
        """Set up test data for integration tests."""
        self.client = APIClient()
        
        # Create comprehensive test data
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create skills
        self.python = Skill.objects.create(name='Python', category='backend', proficiency=4)
        self.react = Skill.objects.create(name='React', category='frontend', proficiency=3)
        self.django = Skill.objects.create(name='Django', category='backend', proficiency=3)
        
        # Create projects
        self.project1 = Project.objects.create(
            title='Full Stack Web App',
            description='A comprehensive web application',
            featured=True
        )
        self.project1.technologies.add(self.python, self.django, self.react)
    
    def test_api_endpoints_accessibility(self):
        """Test that all portfolio API endpoints are accessible."""
        endpoints = [
            reverse('portfolio:project-list'),
            reverse('portfolio:skill-list'),
            reverse('portfolio:skills-by-category'),
            reverse('portfolio:portfolio-stats'),
        ]
        
        for endpoint in endpoints:
            response = self.client.get(endpoint)
            self.assertIn(
                response.status_code,
                [status.HTTP_200_OK, status.HTTP_201_CREATED],
                f"Endpoint {endpoint} returned {response.status_code}"
            )
    
    def test_cross_endpoint_data_consistency(self):
        """Test data consistency across different endpoints."""
        # Get project list
        projects_response = self.client.get(reverse('portfolio:project-list'))
        projects_count = len(projects_response.data['results'])
        
        # Get portfolio stats
        stats_response = self.client.get(reverse('portfolio:portfolio-stats'))
        stats_projects_count = stats_response.data['total_projects']
        
        # Counts should match
        self.assertEqual(projects_count, stats_projects_count)
        
        # Get skills list
        skills_response = self.client.get(reverse('portfolio:skill-list'))
        skills_count = len(skills_response.data['results'])
        
        # Skills count should match stats
        stats_skills_count = stats_response.data['total_skills']
        self.assertEqual(skills_count, stats_skills_count)


# Additional test utilities and fixtures
@pytest.fixture
def api_client():
    """Pytest fixture for API client."""
    return APIClient()


@pytest.fixture
def test_user():
    """Pytest fixture for test user."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def sample_project(test_user):
    """Pytest fixture for sample project."""
    return Project.objects.create(
        title='Sample Project',
        description='A sample project for testing',
        status='completed'
    )


@pytest.fixture
def sample_skill():
    """Pytest fixture for sample skill."""
    return Skill.objects.create(
        name='Sample Skill',
        category='Testing',
        proficiency=75
    )


# Pytest-style test functions
@pytest.mark.django_db
def test_project_list_api_with_fixtures(api_client, sample_project):
    """Test project list API using pytest fixtures."""
    url = reverse('portfolio:project-list')
    response = api_client.get(url)
    
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 1
    assert response.data['results'][0]['title'] == 'Sample Project'


@pytest.mark.django_db
def test_skill_list_api_with_fixtures(api_client, sample_skill):
    """Test skill list API using pytest fixtures."""
    url = reverse('portfolio:skill-list')
    response = api_client.get(url)
    
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 1
    assert response.data['results'][0]['name'] == 'Sample Skill'
