"""
Pytest configuration and fixtures for Django testing.
"""
import pytest


# ============================================================================
# PYTEST CONFIGURATION
# ============================================================================

@pytest.fixture(autouse=True)
def enable_db_access_for_all_tests(db):
    """
    Automatically enable database access for all tests.
    
    This fixture ensures that all tests have database access without
    needing to explicitly mark them with @pytest.mark.django_db.
    """
    pass


# ============================================================================
# CLIENT FIXTURES
# ============================================================================

@pytest.fixture
def client():
    """Standard Django test client."""
    from django.test import Client
    return Client()


@pytest.fixture
def api_client():
    """Django REST Framework API client."""
    from rest_framework.test import APIClient
    return APIClient()


@pytest.fixture
def authenticated_api_client(api_client, test_user):
    """API client authenticated with test user."""
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(test_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


@pytest.fixture
def admin_api_client(api_client, admin_user):
    """API client authenticated with admin user."""
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(admin_user)
    api_client.credentials(HTTP_AUTHORIZATION=f'Bearer {refresh.access_token}')
    return api_client


# ============================================================================
# USER FIXTURES
# ============================================================================

@pytest.fixture
def test_user():
    """Create a standard test user."""
    from django.contrib.auth.models import User
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123',
        first_name='Test',
        last_name='User'
    )


@pytest.fixture
def admin_user():
    """Create an admin test user."""
    from django.contrib.auth.models import User
    return User.objects.create_superuser(
        username='admin',
        email='admin@example.com',
        password='adminpass123',
        first_name='Admin',
        last_name='User'
    )


@pytest.fixture
def staff_user():
    """Create a staff test user."""
    from django.contrib.auth.models import User
    return User.objects.create_user(
        username='staff',
        email='staff@example.com',
        password='staffpass123',
        first_name='Staff',
        last_name='User',
        is_staff=True
    )


# ============================================================================
# BLOG APP FIXTURES
# ============================================================================

@pytest.fixture
def blog_category():
    """Create a test blog category."""
    from blog.models import Category
    return Category.objects.create(
        name='Technology',
        slug='technology',
        description='Technology-related blog posts'
    )


@pytest.fixture
def blog_tag():
    """Create a test blog tag."""
    from blog.models import Tag
    return Tag.objects.create(
        name='Python',
        slug='python'
    )


@pytest.fixture
def blog_post(test_user, blog_category):
    """Create a test blog post."""
    from blog.models import BlogPost
    return BlogPost.objects.create(
        title='Test Blog Post',
        slug='test-blog-post',
        content='This is test content for the blog post.',
        excerpt='Test excerpt for the blog post.',
        author=test_user,
        category=blog_category,
        status='published',
        featured=False,
        read_time=5,
        views=100
    )


# ============================================================================
# PORTFOLIO APP FIXTURES
# ============================================================================

@pytest.fixture
def skill():
    """Create a test skill."""
    from portfolio.models import Skill
    return Skill.objects.create(
        name='Python',
        category='Programming Languages',
        proficiency=90,
        description='Advanced Python programming skills',
        featured=True
    )


@pytest.fixture
def project():
    """Create a test project."""
    from portfolio.models import Project
    return Project.objects.create(
        title='Test Project',
        description='A test project for testing purposes',
        status='completed',
        featured=True,
        github_url='https://github.com/test/project',
        live_url='https://test-project.com'
    )


@pytest.fixture
def portfolio_skills(db, test_user):
    """Create test skills for portfolio tests."""
    from portfolio.models import Skill
    
    skills = []
    skill_data = [
        {
            'name': 'Python',
            'category': 'backend',
            'proficiency': 4
        },
        {
            'name': 'JavaScript',
            'category': 'frontend',
            'proficiency': 3
        },
        {
            'name': 'PostgreSQL',
            'category': 'database',
            'proficiency': 3
        },
        {
            'name': 'Docker',
            'category': 'tools',
            'proficiency': 2
        }
    ]
    
    for data in skill_data:
        skills.append(Skill.objects.create(**data))
    
    return skills


@pytest.fixture
def portfolio_projects(db, test_user, portfolio_skills):
    """Create test projects for portfolio tests."""
    from portfolio.models import Project
    
    projects = []
    project_data = [
        {
            'title': 'E-commerce Platform',
            'description': 'Full-stack e-commerce solution',
            'detailed_description': 'A comprehensive e-commerce platform built with Django and React',
            'github_url': 'https://github.com/user/ecommerce',
            'live_url': 'https://ecommerce.example.com',
            'featured': True
        },
        {
            'title': 'Task Management App',
            'description': 'Project management and task tracking',
            'detailed_description': 'A collaborative task management application',
            'github_url': 'https://github.com/user/taskapp',
            'live_url': 'https://taskapp.example.com',
            'featured': False
        }
    ]
    
    for data in project_data:
        project = Project.objects.create(**data)
        # Add some technologies to the project
        project.technologies.add(*portfolio_skills[:2])
        projects.append(project)
    
    return projects


@pytest.fixture
def portfolio_project(db, test_user, portfolio_skills):
    """Create a single test project for portfolio tests."""
    from portfolio.models import Project
    
    project = Project.objects.create(
        title='Test Project',
        description='A test project for unit testing',
        detailed_description='Detailed description of the test project',
        github_url='https://github.com/user/test-project',
        live_url='https://test-project.example.com',
        featured=True
    )
    # Add some technologies to the project
    project.technologies.add(*portfolio_skills[:2])
    
    return project


@pytest.fixture
def full_test_data(test_user, blog_category, blog_tag, portfolio_skills, portfolio_projects, contact_message):
    """Create comprehensive test data for integration tests."""
    from blog.models import BlogPost
    from portfolio.models import Technology
    
    # Create blog posts
    blog_posts = []
    for i in range(5):
        post = BlogPost.objects.create(
            title=f'Test Blog Post {i+1}',
            slug=f'test-blog-post-{i+1}',
            excerpt=f'Excerpt for test blog post {i+1}',
            content=f'Content for test blog post {i+1}',
            author=test_user,
            category=blog_category,
            status='published',
            featured=(i < 2)
        )
        post.tags.add(blog_tag)
        blog_posts.append(post)
    
    # Create technologies
    technologies = []
    tech_names = ['Python', 'Django', 'React', 'PostgreSQL', 'Docker']
    for name in tech_names:
        tech = Technology.objects.create(
            name=name,
            category='Backend' if name in ['Python', 'Django', 'PostgreSQL'] else 'Frontend'
        )
        technologies.append(tech)
    
    # Associate technologies with projects
    for project in portfolio_projects:
        project.technologies.add(*technologies[:3])
    
    return {
        'user': test_user,
        'blog_posts': blog_posts,
        'skills': portfolio_skills,
        'projects': portfolio_projects,
        'technologies': technologies,
        'contact_message': contact_message
    }


# ============================================================================
# CONTACT APP FIXTURES
# ============================================================================

@pytest.fixture
def contact_message():
    """Create a test contact message."""
    from contact.models import ContactMessage
    return ContactMessage.objects.create(
        name='John Doe',
        email='john@example.com',
        subject='general',
        message='This is a test contact message.',
        status='new',
        ip_address='192.168.1.1',
        user_agent='Mozilla/5.0 Test Browser'
    )


@pytest.fixture
def newsletter_subscription():
    """Create a test newsletter subscription."""
    from contact.models import Newsletter
    return Newsletter.objects.create(
        email='subscriber@example.com',
        name='Newsletter Subscriber',
        is_active=True,
        ip_address='192.168.1.200'
    )


# ============================================================================
# CUSTOM PYTEST MARKERS
# ============================================================================

def pytest_configure(config):
    """Configure custom pytest markers."""
    config.addinivalue_line(
        "markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')"
    )
    config.addinivalue_line(
        "markers", "integration: marks tests as integration tests"
    )
    config.addinivalue_line(
        "markers", "api: marks tests as API tests"
    )
    config.addinivalue_line(
        "markers", "unit: marks tests as unit tests"
    )