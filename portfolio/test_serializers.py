"""
Comprehensive pytest tests for portfolio application serializers.

This module provides thorough testing for all portfolio DRF serializers including:
- SkillSerializer: skill data serialization and validation
- ProjectSerializer: project serialization with nested relationships
- ProjectImageSerializer: project image serialization and validation

Tests cover:
- Serialization of model instances to JSON
- Deserialization and validation of input data
- Field validation and constraints
- Nested serializer relationships
- Choice field validation
- Custom validation methods
- Error handling and validation messages
"""

import pytest
from django.test import TestCase
from rest_framework import serializers
from portfolio.models import Skill, Project, ProjectImage
from portfolio.serializers import SkillSerializer, ProjectSerializer, ProjectImageSerializer
from datetime import datetime


@pytest.mark.django_db
class TestSkillSerializer:
    """Test cases for the SkillSerializer."""
    
    @pytest.fixture
    def skill_data(self):
        """Sample skill data for testing."""
        return {
            'name': 'Python',
            'category': 'backend',
            'proficiency': 4
        }
    
    def test_skill_serialization(self):
        """Test serializing a skill instance."""
        skill = Skill.objects.create(
            name='Django',
            category='backend',
            proficiency=3
        )
        
        serializer = SkillSerializer(skill)
        data = serializer.data
        
        assert data['id'] == skill.id
        assert data['name'] == 'Django'
        assert data['category'] == 'backend'
        assert data['proficiency'] == 3
        assert data['get_category_display'] == 'Backend'
        assert data['get_proficiency_display'] == 'Advanced'
        assert 'created_at' in data
    
    def test_skill_deserialization_valid(self, skill_data):
        """Test deserializing valid skill data."""
        serializer = SkillSerializer(data=skill_data)
        
        assert serializer.is_valid(), serializer.errors
        skill = serializer.save()
        
        assert skill.name == 'Python'
        assert skill.category == 'backend'
        assert skill.proficiency == 4
    
    def test_skill_deserialization_invalid_name(self, skill_data):
        """Test deserializing skill with invalid name."""
        skill_data['name'] = ''  # Empty name
        
        serializer = SkillSerializer(data=skill_data)
        assert not serializer.is_valid()
        assert 'name' in serializer.errors
    
    def test_skill_category_choices_validation(self, skill_data):
        """Test skill category choices validation."""
        # Valid categories
        valid_categories = ['frontend', 'backend', 'database', 'tools']
        
        for category in valid_categories:
            skill_data['category'] = category
            serializer = SkillSerializer(data=skill_data)
            assert serializer.is_valid(), f"Category {category} should be valid"
        
        # Invalid category
        skill_data['category'] = 'invalid_category'
        serializer = SkillSerializer(data=skill_data)
        assert not serializer.is_valid()
        assert 'category' in serializer.errors
    
    def test_skill_proficiency_choices_validation(self, skill_data):
        """Test skill proficiency level choices validation."""
        # Valid proficiency levels
        valid_levels = [1, 2, 3, 4]
        
        for level in valid_levels:
            skill_data['proficiency'] = level
            serializer = SkillSerializer(data=skill_data)
            assert serializer.is_valid(), f"Proficiency level {level} should be valid"
        
        # Invalid proficiency levels
        invalid_levels = [0, 5, -1, 10]
        
        for level in invalid_levels:
            skill_data['proficiency'] = level
            serializer = SkillSerializer(data=skill_data)
            assert not serializer.is_valid(), f"Proficiency level {level} should be invalid"
            assert 'proficiency' in serializer.errors
    
    def test_skill_display_methods(self):
        """Test that display methods are included in serialized data."""
        skill = Skill.objects.create(
            name='React',
            category='frontend',
            proficiency=2
        )
        
        serializer = SkillSerializer(skill)
        data = serializer.data
        
        assert data['get_category_display'] == 'Frontend'
        assert data['get_proficiency_display'] == 'Intermediate'
    
    def test_skill_update(self):
        """Test updating a skill through serializer."""
        skill = Skill.objects.create(
            name='JavaScript',
            category='frontend',
            proficiency=2
        )
        
        update_data = {
            'name': 'Advanced JavaScript',
            'category': 'frontend',
            'proficiency': 4
        }
        
        serializer = SkillSerializer(skill, data=update_data)
        assert serializer.is_valid()
        
        updated_skill = serializer.save()
        assert updated_skill.name == 'Advanced JavaScript'
        assert updated_skill.proficiency == 4


@pytest.mark.django_db
class TestProjectSerializer:
    """Test cases for the ProjectSerializer."""
    
    @pytest.fixture
    def skills(self):
        """Create test skills."""
        return [
            Skill.objects.create(name='Python', category='backend', proficiency=4),
            Skill.objects.create(name='Django', category='backend', proficiency=3),
            Skill.objects.create(name='React', category='frontend', proficiency=3)
        ]
    
    @pytest.fixture
    def project_data(self, skills):
        """Sample project data for testing."""
        return {
            'title': 'E-Commerce Platform',
            'description': 'A full-stack e-commerce solution',
            'detailed_description': 'Complete e-commerce platform with user authentication, product catalog, shopping cart, and payment processing.',
            'github_url': 'https://github.com/user/ecommerce',
            'live_url': 'https://ecommerce-demo.com',
            'technologies': [skill.id for skill in skills[:2]],  # First 2 skills
            'featured': True
        }
    
    def test_project_serialization(self, skills):
        """Test serializing a project instance."""
        project = Project.objects.create(
            title='Portfolio Website',
            description='Personal portfolio website',
            detailed_description='A responsive portfolio website showcasing my projects and skills.',
            github_url='https://github.com/user/portfolio',
            live_url='https://myportfolio.com',
            featured=True
        )
        project.technologies.set(skills)
        
        serializer = ProjectSerializer(project)
        data = serializer.data
        
        assert data['id'] == project.id
        assert data['title'] == 'Portfolio Website'
        assert data['slug'] == 'portfolio-website'
        assert data['description'] == 'Personal portfolio website'
        assert data['detailed_description'] == 'A responsive portfolio website showcasing my projects and skills.'
        assert data['github_url'] == 'https://github.com/user/portfolio'
        assert data['live_url'] == 'https://myportfolio.com'
        assert data['featured'] is True
        assert len(data['technologies']) == 3
        assert 'created_at' in data
        assert 'updated_at' in data
    
    def test_project_deserialization_valid(self, project_data):
        """Test deserializing valid project data."""
        serializer = ProjectSerializer(data=project_data)
        
        assert serializer.is_valid(), serializer.errors
        project = serializer.save()
        
        assert project.title == 'E-Commerce Platform'
        assert project.slug == 'e-commerce-platform'
        assert project.description == 'A full-stack e-commerce solution'
        assert project.detailed_description.startswith('Complete e-commerce platform')
        assert project.github_url == 'https://github.com/user/ecommerce'
        assert project.live_url == 'https://ecommerce-demo.com'
        assert project.featured is True
        assert project.technologies.count() == 2
    
    def test_project_deserialization_minimal_data(self):
        """Test deserializing project with minimal required data."""
        minimal_data = {
            'title': 'Minimal Project',
            'description': 'A minimal project description'
        }
        
        serializer = ProjectSerializer(data=minimal_data)
        assert serializer.is_valid(), serializer.errors
        
        project = serializer.save()
        assert project.title == 'Minimal Project'
        assert project.slug == 'minimal-project'
        assert project.description == 'A minimal project description'
        assert project.detailed_description == ''
        assert project.github_url == ''
        assert project.live_url == ''
        assert project.featured is False
        assert project.technologies.count() == 0
    
    def test_project_deserialization_invalid_title(self, project_data):
        """Test deserializing project with invalid title."""
        project_data['title'] = ''  # Empty title
        
        serializer = ProjectSerializer(data=project_data)
        assert not serializer.is_valid()
        assert 'title' in serializer.errors
    
    def test_project_deserialization_invalid_description(self, project_data):
        """Test deserializing project with invalid description."""
        project_data['description'] = ''  # Empty description
        
        serializer = ProjectSerializer(data=project_data)
        assert not serializer.is_valid()
        assert 'description' in serializer.errors
    
    def test_project_deserialization_invalid_technologies(self, project_data):
        """Test deserializing project with invalid technologies."""
        project_data['technologies'] = [99999]  # Non-existent skill ID
        
        serializer = ProjectSerializer(data=project_data)
        assert not serializer.is_valid()
        assert 'technologies' in serializer.errors
    
    def test_project_url_validation(self, project_data):
        """Test URL field validation."""
        # Valid URLs
        valid_urls = [
            'https://github.com/user/repo',
            'http://example.com',
            'https://subdomain.example.com/path',
            ''  # Empty URL is allowed
        ]
        
        for url in valid_urls:
            project_data['github_url'] = url
            project_data['live_url'] = url
            serializer = ProjectSerializer(data=project_data)
            assert serializer.is_valid(), f"URL {url} should be valid"
        
        # Invalid URLs
        invalid_urls = [
            'not-a-url',
            'ftp://invalid-protocol.com',
            'javascript:alert("xss")'
        ]
        
        for url in invalid_urls:
            project_data['github_url'] = url
            serializer = ProjectSerializer(data=project_data)
            assert not serializer.is_valid(), f"URL {url} should be invalid"
    
    def test_project_nested_technologies_serialization(self, skills):
        """Test nested technologies serialization."""
        project = Project.objects.create(
            title='Full Stack App',
            description='Full stack application'
        )
        project.technologies.set(skills)
        
        serializer = ProjectSerializer(project)
        data = serializer.data
        
        assert 'technologies' in data
        assert len(data['technologies']) == 3
        
        # Check nested skill data
        for tech_data in data['technologies']:
            assert 'id' in tech_data
            assert 'name' in tech_data
            assert 'category' in tech_data
            assert 'proficiency' in tech_data
            assert 'get_category_display' in tech_data
            assert 'get_proficiency_display' in tech_data
    
    def test_project_update(self, skills):
        """Test updating a project through serializer."""
        project = Project.objects.create(
            title='Original Title',
            description='Original description',
            featured=False
        )
        
        update_data = {
            'title': 'Updated Title',
            'description': 'Updated description',
            'detailed_description': 'Added detailed description',
            'github_url': 'https://github.com/user/updated',
            'technologies': [skills[0].id, skills[1].id],
            'featured': True
        }
        
        serializer = ProjectSerializer(project, data=update_data, partial=True)
        assert serializer.is_valid()
        
        updated_project = serializer.save()
        assert updated_project.title == 'Updated Title'
        assert updated_project.slug == 'updated-title'
        assert updated_project.description == 'Updated description'
        assert updated_project.detailed_description == 'Added detailed description'
        assert updated_project.github_url == 'https://github.com/user/updated'
        assert updated_project.featured is True
        assert updated_project.technologies.count() == 2


@pytest.mark.django_db
class TestProjectImageSerializer:
    """Test cases for the ProjectImageSerializer."""
    
    @pytest.fixture
    def project(self):
        """Create a test project."""
        return Project.objects.create(
            title='Test Project',
            description='A test project for image testing'
        )
    
    @pytest.fixture
    def project_image_data(self, project):
        """Sample project image data for testing."""
        return {
            'project': project.id,
            'caption': 'Homepage screenshot',
            'order': 1
        }
    
    def test_project_image_serialization(self, project):
        """Test serializing a project image instance."""
        project_image = ProjectImage.objects.create(
            project=project,
            caption='Dashboard view',
            order=2
        )
        
        serializer = ProjectImageSerializer(project_image)
        data = serializer.data
        
        assert data['id'] == project_image.id
        assert data['project'] == project.id
        assert data['caption'] == 'Dashboard view'
        assert data['order'] == 2
        assert 'image' in data
    
    def test_project_image_deserialization_valid(self, project_image_data):
        """Test deserializing valid project image data."""
        serializer = ProjectImageSerializer(data=project_image_data)
        
        assert serializer.is_valid(), serializer.errors
        project_image = serializer.save()
        
        assert project_image.caption == 'Homepage screenshot'
        assert project_image.order == 1
    
    def test_project_image_deserialization_minimal_data(self, project):
        """Test deserializing project image with minimal data."""
        minimal_data = {
            'project': project.id
        }
        
        serializer = ProjectImageSerializer(data=minimal_data)
        assert serializer.is_valid(), serializer.errors
        
        project_image = serializer.save()
        assert project_image.project == project
        assert project_image.caption == ''
        assert project_image.order == 0  # Default value
    
    def test_project_image_deserialization_invalid_project(self, project_image_data):
        """Test deserializing project image with invalid project."""
        project_image_data['project'] = 99999  # Non-existent project ID
        
        serializer = ProjectImageSerializer(data=project_image_data)
        assert not serializer.is_valid()
        assert 'project' in serializer.errors
    
    def test_project_image_order_validation(self, project_image_data):
        """Test project image order field validation."""
        # Valid order values
        valid_orders = [0, 1, 5, 10, 100]
        
        for order in valid_orders:
            project_image_data['order'] = order
            serializer = ProjectImageSerializer(data=project_image_data)
            assert serializer.is_valid(), f"Order {order} should be valid"
        
        # Invalid order values (negative numbers)
        invalid_orders = [-1, -5, -10]
        
        for order in invalid_orders:
            project_image_data['order'] = order
            serializer = ProjectImageSerializer(data=project_image_data)
            assert not serializer.is_valid(), f"Order {order} should be invalid"
    
    def test_project_image_update(self, project):
        """Test updating a project image through serializer."""
        project_image = ProjectImage.objects.create(
            project=project,
            caption='Original caption',
            order=1
        )
        
        update_data = {
            'caption': 'Updated caption',
            'order': 5
        }
        
        serializer = ProjectImageSerializer(project_image, data=update_data, partial=True)
        assert serializer.is_valid()
        
        updated_image = serializer.save()
        assert updated_image.caption == 'Updated caption'
        assert updated_image.order == 5


@pytest.mark.django_db
class TestPortfolioSerializerIntegration:
    """Integration tests for portfolio serializers working together."""
    
    @pytest.fixture
    def complete_portfolio_setup(self):
        """Create complete portfolio setup with all related objects."""
        # Create skills
        skills = [
            Skill.objects.create(name='Python', category='backend', proficiency=4),
            Skill.objects.create(name='Django', category='backend', proficiency=4),
            Skill.objects.create(name='React', category='frontend', proficiency=3),
            Skill.objects.create(name='PostgreSQL', category='database', proficiency=3)
        ]
        
        # Create project
        project = Project.objects.create(
            title='Full Stack Web Application',
            description='A comprehensive web application',
            detailed_description='Built with Django REST API backend and React frontend, featuring user authentication, real-time updates, and responsive design.',
            github_url='https://github.com/user/fullstack-app',
            live_url='https://fullstack-demo.com',
            featured=True
        )
        project.technologies.set(skills)
        
        # Create project images
        images = [
            ProjectImage.objects.create(
                project=project,
                caption='Homepage with hero section',
                order=1
            ),
            ProjectImage.objects.create(
                project=project,
                caption='User dashboard',
                order=2
            ),
            ProjectImage.objects.create(
                project=project,
                caption='Mobile responsive view',
                order=3
            )
        ]
        
        return {
            'skills': skills,
            'project': project,
            'images': images
        }
    
    def test_complete_project_serialization(self, complete_portfolio_setup):
        """Test serializing a complete project with all relationships."""
        project = complete_portfolio_setup['project']
        
        serializer = ProjectSerializer(project)
        data = serializer.data
        
        # Verify all nested data is present
        assert 'technologies' in data
        assert len(data['technologies']) == 4
        
        # Verify nested skill data structure
        for tech_data in data['technologies']:
            assert 'name' in tech_data
            assert 'category' in tech_data
            assert 'proficiency' in tech_data
            assert 'get_category_display' in tech_data
            assert 'get_proficiency_display' in tech_data
        
        # Verify project data
        assert data['title'] == 'Full Stack Web Application'
        assert data['featured'] is True
        assert data['github_url'] == 'https://github.com/user/fullstack-app'
        assert data['live_url'] == 'https://fullstack-demo.com'
    
    def test_project_with_images_relationship(self, complete_portfolio_setup):
        """Test project and images relationship through serializers."""
        project = complete_portfolio_setup['project']
        images = complete_portfolio_setup['images']
        
        # Serialize project
        project_serializer = ProjectSerializer(project)
        project_data = project_serializer.data
        
        # Serialize images
        images_serializer = ProjectImageSerializer(images, many=True)
        images_data = images_serializer.data
        
        # Verify relationships
        assert len(images_data) == 3
        for image_data in images_data:
            assert image_data['project'] == project.id
        
        # Verify image ordering
        assert images_data[0]['order'] == 1
        assert images_data[1]['order'] == 2
        assert images_data[2]['order'] == 3
    
    def test_skill_project_many_to_many_serialization(self, complete_portfolio_setup):
        """Test many-to-many relationship serialization between skills and projects."""
        skills = complete_portfolio_setup['skills']
        project = complete_portfolio_setup['project']
        
        # Create another project using some of the same skills
        project2 = Project.objects.create(
            title='API Service',
            description='REST API service'
        )
        project2.technologies.set(skills[:2])  # Use first 2 skills
        
        # Serialize both projects
        project1_serializer = ProjectSerializer(project)
        project2_serializer = ProjectSerializer(project2)
        
        project1_data = project1_serializer.data
        project2_data = project2_serializer.data
        
        # Verify skill relationships
        assert len(project1_data['technologies']) == 4
        assert len(project2_data['technologies']) == 2
        
        # Verify shared skills appear in both projects
        project1_skill_names = [tech['name'] for tech in project1_data['technologies']]
        project2_skill_names = [tech['name'] for tech in project2_data['technologies']]
        
        assert 'Python' in project1_skill_names
        assert 'Django' in project1_skill_names
        assert 'Python' in project2_skill_names
        assert 'Django' in project2_skill_names
    
    def test_serializer_validation_with_relationships(self, complete_portfolio_setup):
        """Test validation across related serializers."""
        skills = complete_portfolio_setup['skills']
        
        # Test creating project with existing skills
        project_data = {
            'title': 'New Project',
            'description': 'A new project using existing skills',
            'technologies': [skills[0].id, skills[2].id],  # Python and React
            'featured': False
        }
        
        serializer = ProjectSerializer(data=project_data)
        assert serializer.is_valid(), serializer.errors
        
        new_project = serializer.save()
        assert new_project.title == 'New Project'
        assert new_project.technologies.count() == 2
        
        # Verify the correct skills are associated
        project_skills = list(new_project.technologies.all())
        assert skills[0] in project_skills  # Python
        assert skills[2] in project_skills  # React