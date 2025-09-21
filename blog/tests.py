"""
Comprehensive pytest unit tests for blog app API views.

This module contains test cases for all blog API endpoints including:
- Blog post listing and filtering
- Blog post detail views
- Blog statistics
- Category and tag filtering
- Search functionality

Test Coverage:
- All API views and endpoints
- Response status codes and data structure
- Filtering, search, and pagination
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
from datetime import datetime, timezone
from blog.models import BlogPost, Category, Tag
from blog.views import BlogPostListView, BlogPostDetailView


@pytest.mark.django_db
class TestBlogPostListView(APITestCase):
    """Test cases for BlogPostListView API endpoint."""
    
    def setUp(self):
        """Set up test data for blog post tests."""
        self.client = APIClient()
        self.url = reverse('blog:post-list')
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test categories
        self.category1 = Category.objects.create(
            name='Technology',
            slug='technology',
            description='Tech-related posts'
        )
        
        self.category2 = Category.objects.create(
            name='Programming',
            slug='programming',
            description='Programming tutorials'
        )
        
        # Create test tags
        self.tag1 = Tag.objects.create(name='Python', slug='python')
        self.tag2 = Tag.objects.create(name='Django', slug='django')
        self.tag3 = Tag.objects.create(name='React', slug='react')
        
        # Create test blog posts
        import time
        self.post1 = BlogPost.objects.create(
            title='First Blog Post',
            slug='first-blog-post',
            content='Content of the first blog post',
            excerpt='Excerpt of first post',
            author=self.user,
            category=self.category1,
            status='published',
            featured=True
        )
        self.post1.tags.add(self.tag1, self.tag2)
        
        # Add a small delay to ensure different timestamps
        time.sleep(0.01)
        
        self.post2 = BlogPost.objects.create(
            title='Second Blog Post',
            slug='second-blog-post',
            content='Content of the second blog post',
            excerpt='Excerpt of second post',
            author=self.user,
            category=self.category2,
            status='published',
            featured=False
        )
        self.post2.tags.add(self.tag3)
        
        self.post3 = BlogPost.objects.create(
            title='Draft Post',
            slug='draft-post',
            content='Content of draft post',
            excerpt='Excerpt of draft post',
            author=self.user,
            category=self.category1,
            status='draft',
            featured=False
        )
    
    def test_get_blog_post_list_success(self):
        """Test successful retrieval of blog post list."""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, dict)
        self.assertIn('results', response.data)
        
        # Should only return published posts (not draft)
        results = response.data['results']
        self.assertEqual(len(results), 2)
        
        # Check blog post data structure
        post_data = results[0]
        expected_fields = [
            'id', 'title', 'slug', 'content', 'excerpt', 'author',
            'category', 'tags', 'featured', 'created_at', 'published_at'
        ]
        for field in expected_fields:
            self.assertIn(field, post_data)
    
    def test_blog_post_list_filtering_by_category(self):
        """Test filtering blog posts by category."""
        # Create test blog posts with different categories
        response = self.client.get(self.url, {'category__slug': self.category1.slug})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['category'], 'Technology')
    
    def test_blog_post_list_filtering_by_tags(self):
        """Test filtering blog posts by tags."""
        response = self.client.get(self.url, {'tags__slug': self.tag1.slug})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        self.assertEqual(len(results), 1)
        self.assertIn('Python', results[0]['tags'])
    
    def test_blog_post_list_filtering_by_featured(self):
        """Test filtering blog posts by featured status."""
        response = self.client.get(self.url, {'featured': 'true'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'First Blog Post')
        self.assertTrue(results[0]['featured'])
    
    def test_blog_post_list_search_functionality(self):
        """Test search functionality across blog post fields."""
        response = self.client.get(self.url, {'search': 'First Blog'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0]['title'], 'First Blog Post')
    
    def test_blog_post_list_ordering(self):
        """Test ordering functionality."""
        response = self.client.get(self.url, {'ordering': 'title'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        self.assertEqual(len(results), 2)
        self.assertEqual(results[0]['title'], 'First Blog Post')
        self.assertEqual(results[1]['title'], 'Second Blog Post')
    
    def test_blog_post_list_reverse_ordering(self):
        """Test reverse ordering functionality."""
        response = self.client.get(self.url, {'ordering': '-created_at'})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        results = response.data['results']
        self.assertEqual(len(results), 2)
        # Most recent first - check that first post is newer or equal to second
        from datetime import datetime
        first_created = datetime.fromisoformat(results[0]['created_at'].replace('Z', '+00:00'))
        second_created = datetime.fromisoformat(results[1]['created_at'].replace('Z', '+00:00'))
        self.assertGreaterEqual(first_created, second_created)
    
    def test_blog_post_list_pagination(self):
        """Test pagination functionality."""
        # Create more posts to test pagination
        for i in range(15):
            BlogPost.objects.create(
                title=f'Test Post {i}',
                slug=f'test-post-{i}',
                content=f'Content {i}',
                excerpt=f'Excerpt {i}',
                author=self.user,
                category=self.category1,
                status='published'
            )
        
        response = self.client.get(self.url, {'page_size': 10})
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('next', response.data)
        self.assertIn('previous', response.data)
        self.assertEqual(len(response.data['results']), 10)
    
    def test_blog_post_list_empty_results(self):
        """Test handling of empty results."""
        BlogPost.objects.all().delete()
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 0)


@pytest.mark.django_db
class TestBlogPostDetailView(APITestCase):
    """Test cases for BlogPostDetailView API endpoint."""
    
    def setUp(self):
        """Set up test data for blog post detail tests."""
        self.client = APIClient()
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test category
        self.category = Category.objects.create(
            name='Technology',
            slug='technology',
            description='Tech-related posts'
        )
        
        # Create test tags
        self.tag1 = Tag.objects.create(name='Python', slug='python')
        self.tag2 = Tag.objects.create(name='Django', slug='django')
        
        # Create test blog post
        self.post = BlogPost.objects.create(
            title='Test Blog Post',
            slug='test-blog-post',
            content='Detailed content of the test blog post',
            excerpt='Test excerpt',
            author=self.user,
            category=self.category,
            status='published',
            featured=True
        )
        self.post.tags.add(self.tag1, self.tag2)
        
        self.url = reverse('blog:post-detail', kwargs={'slug': self.post.slug})
        
        # Create draft post for testing access
        self.draft_post = BlogPost.objects.create(
            title='Draft Post',
            slug='draft-post',
            content='Draft content',
            excerpt='Draft excerpt',
            author=self.user,
            category=self.category,
            status='draft'
        )
        self.draft_url = reverse('blog:post-detail', kwargs={'slug': self.draft_post.slug})
    
    def test_get_blog_post_detail_success(self):
        """Test successful retrieval of blog post detail."""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, dict)
        
        # Check blog post data structure
        expected_fields = [
            'id', 'title', 'slug', 'content', 'excerpt', 'author',
            'category', 'tags', 'status', 'featured', 'created_at', 'updated_at'
        ]
        for field in expected_fields:
            self.assertIn(field, response.data)
        
        # Verify specific data
        self.assertEqual(response.data['title'], 'Test Blog Post')
        self.assertEqual(response.data['slug'], 'test-blog-post')
        self.assertEqual(response.data['status'], 'published')
    
    def test_get_blog_post_detail_not_found(self):
        """Test retrieval of non-existent blog post."""
        url = reverse('blog:post-detail', kwargs={'slug': 'non-existent-post'})
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_get_draft_post_detail_unauthorized(self):
        """Test that draft posts are not accessible without proper permissions."""
        response = self.client.get(self.draft_url)
        
        # Should return 404 for draft posts when not authenticated as author
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
    
    def test_blog_post_detail_includes_related_data(self):
        """Test that blog post detail includes related category and tags data."""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check category data
        self.assertIn('category', response.data)
        category_data = response.data['category']
        self.assertEqual(category_data['name'], 'Technology')
        self.assertEqual(category_data['slug'], 'technology')
        
        # Check tags data
        self.assertIn('tags', response.data)
        tags_data = response.data['tags']
        self.assertEqual(len(tags_data), 2)
        tag_names = [tag['name'] for tag in tags_data]
        self.assertIn('Python', tag_names)
        self.assertIn('Django', tag_names)


@pytest.mark.django_db
class TestBlogStatsView(APITestCase):
    """Test cases for blog_stats function-based view."""
    
    def setUp(self):
        """Set up test data for blog stats tests."""
        self.client = APIClient()
        self.url = reverse('blog:blog-stats')
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test categories
        self.category1 = Category.objects.create(
            name='Technology',
            slug='technology'
        )
        
        self.category2 = Category.objects.create(
            name='Programming',
            slug='programming'
        )
        
        # Create test tags
        self.tag1 = Tag.objects.create(name='Python', slug='python')
        self.tag2 = Tag.objects.create(name='Django', slug='django')
        
        # Create test blog posts
        self.post1 = BlogPost.objects.create(
            title='Published Post 1',
            slug='published-post-1',
            content='Content 1',
            author=self.user,
            category=self.category1,
            status='published'
        )
        
        self.post2 = BlogPost.objects.create(
            title='Published Post 2',
            slug='published-post-2',
            content='Content 2',
            author=self.user,
            category=self.category2,
            status='published'
        )
        
        self.post3 = BlogPost.objects.create(
            title='Draft Post',
            slug='draft-post',
            content='Draft content',
            author=self.user,
            category=self.category1,
            status='draft'
        )
    
    def test_blog_stats_success(self):
        """Test successful retrieval of blog statistics."""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, dict)
        
        # Check expected statistics fields
        expected_fields = [
            'total_posts',
            'published_posts',
            'total_categories',
            'total_tags'
        ]
        
        for field in expected_fields:
            self.assertIn(field, response.data)
    
    def test_blog_stats_values(self):
        """Test the accuracy of blog statistics values."""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify statistics values
        self.assertEqual(response.data['total_posts'], 3)
        self.assertEqual(response.data['published_posts'], 2)
        self.assertEqual(response.data['total_categories'], 2)
        self.assertEqual(response.data['total_tags'], 2)
    
    def test_blog_stats_empty_data(self):
        """Test blog statistics with no data."""
        # Delete all data
        BlogPost.objects.all().delete()
        Category.objects.all().delete()
        Tag.objects.all().delete()
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # All counts should be zero
        self.assertEqual(response.data['total_posts'], 0)
        self.assertEqual(response.data['published_posts'], 0)
        self.assertEqual(response.data['total_categories'], 0)
        self.assertEqual(response.data['total_tags'], 0)


@pytest.mark.django_db
class TestBlogAPIIntegration(APITestCase):
    """Integration tests for blog API endpoints."""
    
    def setUp(self):
        """Set up test data for integration tests."""
        self.client = APIClient()
        
        # Create comprehensive test data
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create categories
        self.tech_category = Category.objects.create(
            name='Technology',
            slug='technology',
            description='Technology posts'
        )
        
        # Create tags
        self.python_tag = Tag.objects.create(name='Python', slug='python')
        self.django_tag = Tag.objects.create(name='Django', slug='django')
        
        # Create blog posts
        self.featured_post = BlogPost.objects.create(
            title='Featured Tech Post',
            slug='featured-tech-post',
            content='Comprehensive technology content',
            excerpt='Tech excerpt',
            author=self.user,
            category=self.tech_category,
            status='published',
            featured=True
        )
        self.featured_post.tags.add(self.python_tag, self.django_tag)
    
    def test_api_endpoints_accessibility(self):
        """Test that all blog API endpoints are accessible."""
        endpoints = [
            reverse('blog:post-list'),
            reverse('blog:post-detail', kwargs={'slug': self.featured_post.slug}),
            reverse('blog:blog-stats'),
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
        # Get blog list
        list_response = self.client.get(reverse('blog:post-list'))
        list_posts_count = len(list_response.data['results'])
        
        # Get blog stats
        stats_response = self.client.get(reverse('blog:blog-stats'))
        stats_published_count = stats_response.data['published_posts']
        
        # Published counts should match
        self.assertEqual(list_posts_count, stats_published_count)
        
        # Get specific post detail
        detail_response = self.client.get(
            reverse('blog:post-detail', kwargs={'slug': self.featured_post.slug})
        )
        
        # Post data should be consistent
        list_post = list_response.data['results'][0]
        detail_post = detail_response.data
        
        self.assertEqual(list_post['id'], detail_post['id'])
        self.assertEqual(list_post['title'], detail_post['title'])
        self.assertEqual(list_post['slug'], detail_post['slug'])
    
    def test_filtering_and_search_integration(self):
        """Test integration of filtering and search across endpoints."""
        # Create additional test data
        BlogPost.objects.create(
            title='Another Tech Post',
            slug='another-tech-post',
            content='More technology content',
            author=self.user,
            category=self.tech_category,
            status='published'
        )
        
        # Test category filtering
        category_response = self.client.get(
            reverse('blog:post-list'),
            {'category__slug': 'technology'}
        )
        self.assertEqual(len(category_response.data.get('results', category_response.data)), 2)
        
        # Test search functionality
        search_response = self.client.get(
            reverse('blog:post-list'),
            {'search': 'Featured'}
        )
        self.assertEqual(len(search_response.data.get('results', search_response.data)), 1)
        if 'results' in search_response.data:
            self.assertEqual(search_response.data['results'][0]['title'], 'Featured Tech Post')
        else:
            self.assertEqual(search_response.data[0]['title'], 'Featured Tech Post')


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
def sample_category():
    """Pytest fixture for sample category."""
    return Category.objects.create(
        name='Sample Category',
        slug='sample-category',
        description='A sample category for testing'
    )


@pytest.fixture
def sample_tag():
    """Pytest fixture for sample tag."""
    return Tag.objects.create(name='Sample Tag', slug='sample-tag')


@pytest.fixture
def sample_blog_post(test_user, sample_category):
    """Pytest fixture for sample blog post."""
    return BlogPost.objects.create(
        title='Sample Blog Post',
        slug='sample-blog-post',
        content='Sample content for testing',
        excerpt='Sample excerpt',
        author=test_user,
        category=sample_category,
        status='published'
    )


# Pytest-style test functions
@pytest.mark.django_db
def test_blog_list_api_with_fixtures(api_client, sample_blog_post):
    """Test blog list API using pytest fixtures."""
    url = reverse('blog:post-list')
    response = api_client.get(url)
    
    assert response.status_code == status.HTTP_200_OK
    assert len(response.data['results']) == 1
    assert response.data['results'][0]['title'] == 'Sample Blog Post'


@pytest.mark.django_db
def test_blog_detail_api_with_fixtures(api_client, sample_blog_post):
    """Test blog detail API using pytest fixtures."""
    url = reverse('blog:post-detail', kwargs={'slug': sample_blog_post.slug})
    response = api_client.get(url)
    
    assert response.status_code == status.HTTP_200_OK
    assert response.data['title'] == 'Sample Blog Post'
    assert response.data['slug'] == 'sample-blog-post'


@pytest.mark.django_db
def test_blog_stats_api_with_fixtures(api_client, sample_blog_post):
    """Test blog stats API using pytest fixtures."""
    url = reverse('blog:blog-stats')
    response = api_client.get(url)
    
    assert response.status_code == status.HTTP_200_OK
    assert response.data['total_posts'] == 1
    assert response.data['published_posts'] == 1
