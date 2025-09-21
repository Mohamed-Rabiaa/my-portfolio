"""
Comprehensive pytest tests for portfolio application models.

This module provides thorough testing for all portfolio models including:
- Skill model: creation, categories, proficiency levels, string representation
- Project model: creation, slug generation, relationships, featured status
- ProjectImage model: creation, ordering, relationships with projects

Tests cover:
- Model field validation and constraints
- Automatic slug generation from titles
- Model relationships (ForeignKey, ManyToMany)
- Custom model methods and properties
- String representations
- Model ordering and meta options
- Choice field validation
"""

import pytest
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from datetime import datetime
from portfolio.models import Skill, Project, ProjectImage


@pytest.mark.django_db
class TestSkillModel:
    """Test cases for the Skill model."""
    
    def test_skill_creation(self):
        """Test basic skill creation with all fields."""
        skill = Skill.objects.create(
            name="Python",
            category="backend",
            proficiency=3
        )
        
        assert skill.name == "Python"
        assert skill.category == "backend"
        assert skill.proficiency == 3
        assert skill.created_at is not None
        assert isinstance(skill.created_at, datetime)
    
    def test_skill_category_choices(self):
        """Test skill category choices validation."""
        # Valid categories
        valid_categories = ['frontend', 'backend', 'database', 'tools']
        
        for category in valid_categories:
            skill = Skill.objects.create(
                name=f"Test {category}",
                category=category,
                proficiency=2
            )
            assert skill.category == category
    
    def test_skill_proficiency_choices(self):
        """Test skill proficiency level choices validation."""
        # Valid proficiency levels
        valid_levels = [1, 2, 3, 4]
        
        for level in valid_levels:
            skill = Skill.objects.create(
                name=f"Test Skill {level}",
                category="backend",
                proficiency=level
            )
            assert skill.proficiency == level
    
    def test_skill_get_category_display(self):
        """Test category display names."""
        skill = Skill.objects.create(
            name="React",
            category="frontend",
            proficiency=3
        )
        assert skill.get_category_display() == "Frontend"
        
        skill2 = Skill.objects.create(
            name="Django",
            category="backend",
            proficiency=4
        )
        assert skill2.get_category_display() == "Backend"
    
    def test_skill_get_proficiency_display(self):
        """Test proficiency level display names."""
        skill = Skill.objects.create(
            name="JavaScript",
            category="frontend",
            proficiency=1
        )
        assert skill.get_proficiency_display() == "Beginner"
        
        skill2 = Skill.objects.create(
            name="Python",
            category="backend",
            proficiency=4
        )
        assert skill2.get_proficiency_display() == "Expert"
    
    def test_skill_string_representation(self):
        """Test skill string representation."""
        skill = Skill.objects.create(
            name="PostgreSQL",
            category="database",
            proficiency=3
        )
        assert str(skill) == "PostgreSQL (Database)"
    
    def test_skill_ordering(self):
        """Test skill ordering by category then name."""
        # Create skills in different categories
        Skill.objects.create(name="React", category="frontend", proficiency=3)
        Skill.objects.create(name="Vue", category="frontend", proficiency=2)
        Skill.objects.create(name="Django", category="backend", proficiency=4)
        Skill.objects.create(name="Flask", category="backend", proficiency=3)
        
        skills = list(Skill.objects.all())
        
        # Should be ordered by category first, then name
        assert skills[0].category == "backend" and skills[0].name == "Django"
        assert skills[1].category == "backend" and skills[1].name == "Flask"
        assert skills[2].category == "frontend" and skills[2].name == "React"
        assert skills[3].category == "frontend" and skills[3].name == "Vue"


@pytest.mark.django_db
class TestProjectModel:
    """Test cases for the Project model."""
    
    @pytest.fixture
    def skills(self):
        """Create test skills."""
        return [
            Skill.objects.create(name="Python", category="backend", proficiency=4),
            Skill.objects.create(name="Django", category="backend", proficiency=3),
            Skill.objects.create(name="React", category="frontend", proficiency=3)
        ]
    
    def test_project_creation(self, skills):
        """Test basic project creation."""
        project = Project.objects.create(
            title="My Portfolio Website",
            description="A personal portfolio website",
            detailed_description="A comprehensive portfolio showcasing my work",
            github_url="https://github.com/user/portfolio",
            live_url="https://myportfolio.com",
            featured=True
        )
        
        assert project.title == "My Portfolio Website"
        assert project.slug == "my-portfolio-website"  # Auto-generated
        assert project.description == "A personal portfolio website"
        assert project.detailed_description == "A comprehensive portfolio showcasing my work"
        assert project.github_url == "https://github.com/user/portfolio"
        assert project.live_url == "https://myportfolio.com"
        assert project.featured is True
        assert project.created_at is not None
        assert project.updated_at is not None
        assert isinstance(project.created_at, datetime)
        assert isinstance(project.updated_at, datetime)
    
    def test_project_slug_auto_generation(self):
        """Test automatic slug generation from title."""
        project = Project.objects.create(
            title="E-Commerce Web Application",
            description="Online shopping platform"
        )
        assert project.slug == "e-commerce-web-application"
        
        # Test with special characters
        project2 = Project.objects.create(
            title="AI & Machine Learning Dashboard",
            description="ML dashboard"
        )
        assert project2.slug == "ai-machine-learning-dashboard"
    
    def test_project_custom_slug(self):
        """Test project creation with custom slug."""
        project = Project.objects.create(
            title="My Project",
            slug="custom-project-slug",
            description="Test project"
        )
        assert project.slug == "custom-project-slug"
    
    def test_project_unique_slug_constraint(self):
        """Test that project slugs must be unique."""
        Project.objects.create(
            title="First Project",
            slug="test-project",
            description="First description"
        )
        
        with pytest.raises(IntegrityError):
            Project.objects.create(
                title="Second Project",
                slug="test-project",
                description="Second description"
            )
    
    def test_project_technologies_relationship(self, skills):
        """Test many-to-many relationship with skills."""
        project = Project.objects.create(
            title="Web App",
            description="A web application"
        )
        
        # Add technologies
        project.technologies.add(*skills[:2])  # Add first 2 skills
        
        assert project.technologies.count() == 2
        assert skills[0] in project.technologies.all()
        assert skills[1] in project.technologies.all()
        assert skills[2] not in project.technologies.all()
    
    def test_project_optional_fields(self):
        """Test project creation with optional fields."""
        project = Project.objects.create(
            title="Minimal Project",
            description="Basic project"
        )
        
        assert project.detailed_description == ""
        assert project.github_url == ""
        assert project.live_url == ""
        assert project.image.name == ""
        assert project.featured is False  # Default
    
    def test_project_string_representation(self):
        """Test project string representation."""
        project = Project.objects.create(
            title="Amazing Web App",
            description="An amazing application"
        )
        assert str(project) == "Amazing Web App"
    
    def test_project_ordering(self):
        """Test project ordering by featured status then created_at."""
        # Create projects with different featured status
        regular_project = Project.objects.create(
            title="Regular Project",
            description="Not featured",
            featured=False
        )
        
        featured_project = Project.objects.create(
            title="Featured Project",
            description="This is featured",
            featured=True
        )
        
        projects = list(Project.objects.all())
        
        # Featured projects should come first
        assert projects[0] == featured_project
        assert projects[1] == regular_project
    
    def test_project_featured_default(self):
        """Test that projects are not featured by default."""
        project = Project.objects.create(
            title="Default Project",
            description="Test project"
        )
        assert project.featured is False


@pytest.mark.django_db
class TestProjectImageModel:
    """Test cases for the ProjectImage model."""
    
    @pytest.fixture
    def project(self):
        """Create a test project."""
        return Project.objects.create(
            title="Test Project",
            description="A test project for image testing"
        )
    
    def test_project_image_creation(self, project):
        """Test basic project image creation."""
        project_image = ProjectImage.objects.create(
            project=project,
            caption="Screenshot of the homepage",
            order=1
        )
        
        assert project_image.project == project
        assert project_image.caption == "Screenshot of the homepage"
        assert project_image.order == 1
    
    def test_project_image_optional_caption(self, project):
        """Test project image creation with blank caption."""
        project_image = ProjectImage.objects.create(
            project=project,
            order=1
        )
        
        assert project_image.caption == ""
        assert project_image.order == 1
    
    def test_project_image_default_order(self, project):
        """Test project image default order value."""
        project_image = ProjectImage.objects.create(project=project)
        assert project_image.order == 0  # Default value
    
    def test_project_image_string_representation(self, project):
        """Test project image string representation."""
        project_image = ProjectImage.objects.create(
            project=project,
            order=2
        )
        expected = f"{project.title} - Image 2"
        assert str(project_image) == expected
    
    def test_project_image_ordering(self, project):
        """Test project image ordering by order field."""
        # Create images with different order values
        image3 = ProjectImage.objects.create(project=project, order=3)
        image1 = ProjectImage.objects.create(project=project, order=1)
        image2 = ProjectImage.objects.create(project=project, order=2)
        
        images = list(ProjectImage.objects.all())
        
        # Should be ordered by order field
        assert images[0] == image1
        assert images[1] == image2
        assert images[2] == image3
    
    def test_project_image_relationship(self, project):
        """Test relationship between project image and project."""
        image1 = ProjectImage.objects.create(project=project, order=1)
        image2 = ProjectImage.objects.create(project=project, order=2)
        
        # Test forward relationship
        assert image1.project == project
        assert image2.project == project
        
        # Test reverse relationship
        additional_images = project.additional_images.all()
        assert image1 in additional_images
        assert image2 in additional_images
        assert additional_images.count() == 2
    
    def test_project_image_cascade_delete(self, project):
        """Test that project images are deleted when project is deleted."""
        image1 = ProjectImage.objects.create(project=project, order=1)
        image2 = ProjectImage.objects.create(project=project, order=2)
        
        assert ProjectImage.objects.count() == 2
        
        # Delete the project
        project.delete()
        
        # Images should be deleted too (CASCADE)
        assert ProjectImage.objects.count() == 0


@pytest.mark.django_db
class TestModelIntegration:
    """Integration tests for portfolio models working together."""
    
    def test_project_with_skills_and_images(self):
        """Test creating a complete project with skills and images."""
        # Create skills
        python_skill = Skill.objects.create(
            name="Python",
            category="backend",
            proficiency=4
        )
        react_skill = Skill.objects.create(
            name="React",
            category="frontend",
            proficiency=3
        )
        
        # Create project
        project = Project.objects.create(
            title="Full Stack Web App",
            description="A complete web application",
            detailed_description="Built with Python backend and React frontend",
            github_url="https://github.com/user/webapp",
            live_url="https://webapp.com",
            featured=True
        )
        
        # Add skills to project
        project.technologies.add(python_skill, react_skill)
        
        # Add images to project
        image1 = ProjectImage.objects.create(
            project=project,
            caption="Homepage screenshot",
            order=1
        )
        image2 = ProjectImage.objects.create(
            project=project,
            caption="Dashboard view",
            order=2
        )
        
        # Verify relationships
        assert project.technologies.count() == 2
        assert python_skill in project.technologies.all()
        assert react_skill in project.technologies.all()
        
        assert project.additional_images.count() == 2
        assert image1 in project.additional_images.all()
        assert image2 in project.additional_images.all()
        
        # Verify reverse relationships
        assert project in python_skill.projects.all()
        assert project in react_skill.projects.all()
    
    def test_skill_project_relationship(self):
        """Test the many-to-many relationship between skills and projects."""
        # Create skills
        django_skill = Skill.objects.create(
            name="Django",
            category="backend",
            proficiency=4
        )
        
        # Create multiple projects using the same skill
        project1 = Project.objects.create(
            title="Blog Platform",
            description="Django blog"
        )
        project2 = Project.objects.create(
            title="E-commerce Site",
            description="Django e-commerce"
        )
        
        # Add skill to both projects
        project1.technologies.add(django_skill)
        project2.technologies.add(django_skill)
        
        # Verify relationships
        assert django_skill.projects.count() == 2
        assert project1 in django_skill.projects.all()
        assert project2 in django_skill.projects.all()
        
        assert project1.technologies.count() == 1
        assert project2.technologies.count() == 1