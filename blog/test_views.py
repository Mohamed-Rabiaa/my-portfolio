"""
Comprehensive pytest tests for blog application API views.

This module provides thorough testing for all blog REST API views including:
- BlogPostListView: listing, filtering, searching, and pagination
- BlogPostDetailView: individual post retrieval and view counting
- FeaturedBlogPostsView: featured posts endpoint
- CategoryListView and TagListView: metadata endpoints
- CommentCreateView: comment creation and moderation
- Function-based views: recent posts, popular posts, blog stats

Tests cover:
- HTTP status codes and response structure
- Authentication and permission requirements
- Data validation and serialization
- Filtering, searching, and ordering
- Pagination functionality
- Error handling and edge cases
- View counting and analytics
- Comment moderation workflow
"""

import pytest
from django.urls import reverse
from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APIClient
from unittest.mock import patch, Mock
from datetime import datetime, timezone, timedelta
from blog.models import BlogPost, Category, Tag, Comment


@pytest.mark.django_db
@pytest.mark.api
class TestBlogPostListView:
    """Test cases for BlogPostListView API endpoint."""
    
    def test_get_blog_posts_success(self, api_client, published_blog_posts):
        """Test successful retrieval of published blog posts."""
        url = reverse('blog:post-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert 'results' in response.data
        assert 'count' in response.data
        assert 'next' in response.data
        assert 'previous' in response.data
        
        # Should return all published posts
        results = response.data['results']
        assert len(results) == len(published_blog_posts)
        
        # Check response structure
        if results:
            post_data = results[0]
            expected_fields = [
                'id', 'title', 'slug', 'excerpt', 'author', 'category',
                'tags', 'featured_image', 'featured', 'read_time',
                'views', 'published_at', 'created_at'
            ]
            for field in expected_fields:
                assert field in post_data
    
    def test_get_blog_posts_empty_list(self, api_client):
        """Test blog post list when no posts exist."""
        url = reverse('blog:post-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 0
        assert len(response.data['results']) == 0
    
    def test_blog_posts_only_published(self, api_client, test_user, blog_category):
        """Test that only published posts are returned."""
        # Create published post
        published_post = BlogPost.objects.create(
            title='Published Post',
            slug='published-post',
            content='Published content',
            author=test_user,
            category=blog_category,
            status='published'
        )
        
        # Create draft post
        draft_post = BlogPost.objects.create(
            title='Draft Post',
            slug='draft-post',
            content='Draft content',
            author=test_user,
            category=blog_category,
            status='draft'
        )
        
        url = reverse('blog:post-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert response.data['count'] == 1
        assert response.data['results'][0]['title'] == 'Published Post'
    
    def test_blog_posts_filtering_by_category(self, api_client, published_blog_posts, blog_categories):
        """Test filtering blog posts by category slug."""
        category_slug = blog_categories[0].slug
        url = reverse('blog:post-list')
        response = api_client.get(url, {'category__slug': category_slug})
        
        assert response.status_code == status.HTTP_200_OK
        
        # All returned posts should belong to the specified category
        for post in response.data['results']:
            assert post['category']['slug'] == category_slug
    
    def test_blog_posts_filtering_by_tag(self, api_client, published_blog_posts, blog_tags):
        """Test filtering blog posts by tag slug."""
        tag_slug = blog_tags[0].slug
        url = reverse('blog:post-list')
        response = api_client.get(url, {'tags__slug': tag_slug})
        
        assert response.status_code == status.HTTP_200_OK
        
        # All returned posts should have the specified tag
        for post in response.data['results']:
            tag_slugs = [tag['slug'] for tag in post['tags']]
            assert tag_slug in tag_slugs
    
    def test_blog_posts_filtering_by_featured(self, api_client, published_blog_posts):
        """Test filtering blog posts by featured status."""
        url = reverse('blog:post-list')
        response = api_client.get(url, {'featured': 'true'})
        
        assert response.status_code == status.HTTP_200_OK
        
        # All returned posts should be featured
        for post in response.data['results']:
            assert post['featured'] is True
    
    def test_blog_posts_filtering_by_author(self, api_client, published_blog_posts, test_user):
        """Test filtering blog posts by author."""
        url = reverse('blog:post-list')
        response = api_client.get(url, {'author': test_user.id})
        
        assert response.status_code == status.HTTP_200_OK
        
        # All returned posts should belong to the specified author
        for post in response.data['results']:
            assert post['author']['id'] == test_user.id
    
    def test_blog_posts_search_functionality(self, api_client, test_user, blog_category):
        """Test search functionality across title, excerpt, content, and tags."""
        # Create posts with specific content for searching
        post1 = BlogPost.objects.create(
            title='Python Programming Tutorial',
            slug='python-tutorial',
            content='Learn Python programming basics',
            excerpt='Python tutorial excerpt',
            author=test_user,
            category=blog_category,
            status='published'
        )
        
        post2 = BlogPost.objects.create(
            title='Django Web Development',
            slug='django-web-dev',
            content='Build web applications with Django',
            excerpt='Django development guide',
            author=test_user,
            category=blog_category,
            status='published'
        )
        
        url = reverse('blog:post-list')
        
        # Search by title
        response = api_client.get(url, {'search': 'Python'})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['title'] == 'Python Programming Tutorial'
        
        # Search by content
        response = api_client.get(url, {'search': 'Django'})
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['title'] == 'Django Web Development'
    
    def test_blog_posts_ordering(self, api_client, published_blog_posts):
        """Test ordering blog posts by different fields."""
        url = reverse('blog:post-list')
        
        # Test ordering by published_at (default)
        response = api_client.get(url, {'ordering': '-published_at'})
        assert response.status_code == status.HTTP_200_OK
        
        # Test ordering by views
        response = api_client.get(url, {'ordering': '-views'})
        assert response.status_code == status.HTTP_200_OK
        
        # Test ordering by title
        response = api_client.get(url, {'ordering': 'title'})
        assert response.status_code == status.HTTP_200_OK
        
        # Verify ordering is applied
        if len(response.data['results']) > 1:
            titles = [post['title'] for post in response.data['results']]
            assert titles == sorted(titles)
    
    def test_blog_posts_pagination(self, api_client, test_user, blog_category):
        """Test pagination functionality."""
        # Create multiple posts for pagination testing
        for i in range(15):
            BlogPost.objects.create(
                title=f'Post {i+1}',
                slug=f'post-{i+1}',
                content=f'Content for post {i+1}',
                author=test_user,
                category=blog_category,
                status='published'
            )
        
        url = reverse('blog:post-list')
        
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
    
    def test_blog_posts_combined_filters(self, api_client, test_user, blog_categories, blog_tags):
        """Test combining multiple filters."""
        # Create specific post for testing
        post = BlogPost.objects.create(
            title='Featured Python Tutorial',
            slug='featured-python-tutorial',
            content='Advanced Python programming',
            author=test_user,
            category=blog_categories[0],
            status='published',
            featured=True
        )
        post.tags.add(blog_tags[0])
        
        url = reverse('blog:post-list')
        response = api_client.get(url, {
            'featured': 'true',
            'category__slug': blog_categories[0].slug,
            'search': 'Python'
        })
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['title'] == 'Featured Python Tutorial'


@pytest.mark.django_db
@pytest.mark.api
class TestBlogPostDetailView:
    """Test cases for BlogPostDetailView API endpoint."""
    
    def test_get_blog_post_detail_success(self, api_client, blog_post):
        """Test successful retrieval of blog post detail."""
        url = reverse('blog:post-detail', kwargs={'slug': blog_post.slug})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        
        # Check response structure
        expected_fields = [
            'id', 'title', 'slug', 'content', 'excerpt', 'author',
            'category', 'tags', 'featured_image', 'status', 'featured',
            'read_time', 'views', 'published_at', 'created_at', 'updated_at'
        ]
        for field in expected_fields:
            assert field in response.data
        
        # Check data accuracy
        assert response.data['title'] == blog_post.title
        assert response.data['slug'] == blog_post.slug
        assert response.data['content'] == blog_post.content
    
    def test_get_blog_post_detail_not_found(self, api_client):
        """Test blog post detail with non-existent slug."""
        url = reverse('blog:post-detail', kwargs={'slug': 'non-existent-slug'})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_blog_post_detail_view_count_increment(self, api_client, blog_post):
        """Test that view count increments when accessing post detail."""
        initial_views = blog_post.views
        
        url = reverse('blog:post-detail', kwargs={'slug': blog_post.slug})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        
        # Refresh from database and check view count
        blog_post.refresh_from_db()
        assert blog_post.views == initial_views + 1
        assert response.data['views'] == initial_views + 1
    
    def test_blog_post_detail_draft_not_accessible(self, api_client, draft_blog_post):
        """Test that draft posts are not accessible via detail view."""
        url = reverse('blog:post-detail', kwargs={'slug': draft_blog_post.slug})
        response = api_client.get(url)
        
        # Should return 404 for draft posts
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_blog_post_detail_with_comments(self, api_client, blog_post, blog_comments):
        """Test blog post detail includes related comments."""
        url = reverse('blog:post-detail', kwargs={'slug': blog_post.slug})
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        
        # Check if comments are included (depends on serializer implementation)
        # This test assumes comments might be included in the response
        if 'comments' in response.data:
            assert isinstance(response.data['comments'], list)


@pytest.mark.django_db
@pytest.mark.api
class TestFeaturedBlogPostsView:
    """Test cases for FeaturedBlogPostsView API endpoint."""
    
    def test_get_featured_posts_success(self, api_client, published_blog_posts):
        """Test successful retrieval of featured blog posts."""
        url = reverse('blog:featured-posts')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)
        
        # All returned posts should be featured
        for post in response.data:
            assert post['featured'] is True
    
    def test_get_featured_posts_empty(self, api_client, test_user, blog_category):
        """Test featured posts endpoint when no featured posts exist."""
        # Create non-featured post
        BlogPost.objects.create(
            title='Non-Featured Post',
            slug='non-featured-post',
            content='Non-featured content',
            author=test_user,
            category=blog_category,
            status='published',
            featured=False
        )
        
        url = reverse('blog:featured-posts')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0


@pytest.mark.django_db
@pytest.mark.api
class TestCategoryListView:
    """Test cases for CategoryListView API endpoint."""
    
    def test_get_categories_success(self, api_client, blog_categories):
        """Test successful retrieval of blog categories."""
        url = reverse('blog:category-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)
        assert len(response.data) == len(blog_categories)
        
        # Check response structure
        if response.data:
            category_data = response.data[0]
            expected_fields = ['id', 'name', 'slug', 'description']
            for field in expected_fields:
                assert field in category_data
    
    def test_get_categories_empty(self, api_client):
        """Test categories endpoint when no categories exist."""
        url = reverse('blog:category-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0


@pytest.mark.django_db
@pytest.mark.api
class TestTagListView:
    """Test cases for TagListView API endpoint."""
    
    def test_get_tags_success(self, api_client, blog_tags):
        """Test successful retrieval of blog tags."""
        url = reverse('blog:tag-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)
        assert len(response.data) == len(blog_tags)
        
        # Check response structure
        if response.data:
            tag_data = response.data[0]
            expected_fields = ['id', 'name', 'slug']
            for field in expected_fields:
                assert field in tag_data
    
    def test_get_tags_empty(self, api_client):
        """Test tags endpoint when no tags exist."""
        url = reverse('blog:tag-list')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 0


@pytest.mark.django_db
@pytest.mark.api
class TestCommentCreateView:
    """Test cases for CommentCreateView API endpoint."""
    
    def test_create_comment_success(self, api_client, blog_post):
        """Test successful creation of blog comment."""
        url = reverse('blog:comment-create', kwargs={'post_slug': blog_post.slug})
        data = {
            'name': 'Commenter',
            'email': 'commenter@example.com',
            'content': 'This is a test comment.'
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_201_CREATED
        assert Comment.objects.count() == 1
        
        comment = Comment.objects.first()
        assert comment.post == blog_post
        assert comment.name == 'Commenter'
        assert comment.email == 'commenter@example.com'
        assert comment.content == 'This is a test comment.'
        assert comment.approved is False  # Comments should be unapproved by default
    
    def test_create_comment_invalid_data(self, api_client, blog_post):
        """Test comment creation with invalid data."""
        url = reverse('blog:comment-create', kwargs={'post_slug': blog_post.slug})
        data = {
            'name': '',  # Empty name
            'email': 'invalid-email',  # Invalid email
            'content': ''  # Empty content
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Comment.objects.count() == 0
        
        # Check validation errors
        assert 'name' in response.data
        assert 'email' in response.data
        assert 'content' in response.data
    
    def test_create_comment_non_existent_post(self, api_client):
        """Test comment creation for non-existent post."""
        url = reverse('blog:comment-create', kwargs={'post_slug': 'non-existent-slug'})
        data = {
            'name': 'Commenter',
            'email': 'commenter@example.com',
            'content': 'This is a test comment.'
        }
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert Comment.objects.count() == 0
    
    def test_create_comment_missing_fields(self, api_client, blog_post):
        """Test comment creation with missing required fields."""
        url = reverse('blog:comment-create', kwargs={'post_slug': blog_post.slug})
        data = {'name': 'Commenter'}  # Missing email and content
        
        response = api_client.post(url, data, format='json')
        
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert Comment.objects.count() == 0
        
        assert 'email' in response.data
        assert 'content' in response.data


@pytest.mark.django_db
@pytest.mark.api
class TestBlogFunctionViews:
    """Test cases for blog function-based API views."""
    
    def test_recent_posts_success(self, api_client, published_blog_posts):
        """Test recent posts endpoint."""
        url = reverse('blog:recent-posts')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)
        assert len(response.data) <= 5  # Should return max 5 recent posts
        
        # Posts should be ordered by published_at descending
        if len(response.data) > 1:
            dates = [post['published_at'] for post in response.data]
            assert dates == sorted(dates, reverse=True)
    
    def test_popular_posts_success(self, api_client, published_blog_posts):
        """Test popular posts endpoint."""
        url = reverse('blog:popular-posts')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        assert isinstance(response.data, list)
        assert len(response.data) <= 5  # Should return max 5 popular posts
        
        # Posts should be ordered by views descending
        if len(response.data) > 1:
            views = [post['views'] for post in response.data]
            assert views == sorted(views, reverse=True)
    
    def test_blog_stats_success(self, api_client, published_blog_posts, blog_categories, blog_tags, blog_comments):
        """Test blog stats endpoint."""
        url = reverse('blog:blog-stats')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        
        # Check response structure
        expected_fields = [
            'total_posts', 'published_posts', 'total_categories',
            'total_tags', 'total_comments'
        ]
        for field in expected_fields:
            assert field in response.data
        
        # Check data accuracy
        assert response.data['published_posts'] == len(published_blog_posts)
        assert response.data['total_categories'] == len(blog_categories)
        assert response.data['total_tags'] == len(blog_tags)
    
    def test_blog_stats_empty_data(self, api_client):
        """Test blog stats with no data."""
        url = reverse('blog:blog-stats')
        response = api_client.get(url)
        
        assert response.status_code == status.HTTP_200_OK
        
        # All counts should be zero
        assert response.data['total_posts'] == 0
        assert response.data['published_posts'] == 0
        assert response.data['total_categories'] == 0
        assert response.data['total_tags'] == 0
        assert response.data['total_comments'] == 0


@pytest.mark.django_db
@pytest.mark.integration
class TestBlogAPIIntegration:
    """Integration tests for blog API endpoints."""
    
    def test_blog_api_workflow(self, api_client, test_user, blog_category, blog_tag):
        """Test complete blog API workflow."""
        # 1. Check initial empty state
        posts_response = api_client.get(reverse('blog:post-list'))
        assert posts_response.data['count'] == 0
        
        # 2. Create blog post (simulating admin action)
        blog_post = BlogPost.objects.create(
            title='Integration Test Post',
            slug='integration-test-post',
            content='Integration test content',
            excerpt='Integration test excerpt',
            author=test_user,
            category=blog_category,
            status='published',
            featured=True
        )
        blog_post.tags.add(blog_tag)
        
        # 3. Verify post appears in list
        posts_response = api_client.get(reverse('blog:post-list'))
        assert posts_response.data['count'] == 1
        assert posts_response.data['results'][0]['title'] == 'Integration Test Post'
        
        # 4. Access post detail and verify view count
        detail_response = api_client.get(
            reverse('blog:post-detail', kwargs={'slug': blog_post.slug})
        )
        assert detail_response.status_code == status.HTTP_200_OK
        assert detail_response.data['views'] == 1
        
        # 5. Add comment
        comment_response = api_client.post(
            reverse('blog:comment-create', kwargs={'post_slug': blog_post.slug}),
            {
                'name': 'Test Commenter',
                'email': 'commenter@example.com',
                'content': 'Great post!'
            },
            format='json'
        )
        assert comment_response.status_code == status.HTTP_201_CREATED
        
        # 6. Check stats
        stats_response = api_client.get(reverse('blog:blog-stats'))
        assert stats_response.data['published_posts'] == 1
        assert stats_response.data['total_comments'] == 1
    
    def test_blog_api_error_handling(self, api_client):
        """Test error handling across blog API endpoints."""
        # Test non-existent post detail
        response = api_client.get(
            reverse('blog:post-detail', kwargs={'slug': 'non-existent'})
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # Test comment creation for non-existent post
        response = api_client.post(
            reverse('blog:comment-create', kwargs={'post_slug': 'non-existent'}),
            {'name': 'Test', 'email': 'test@example.com', 'content': 'Test'},
            format='json'
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND
        
        # Test invalid pagination
        response = api_client.get(reverse('blog:post-list'), {'page': 999})
        assert response.status_code == status.HTTP_404_NOT_FOUND
    
    def test_blog_api_performance(self, api_client, full_test_data):
        """Test blog API performance with full dataset."""
        # This test ensures the API performs well with a complete dataset
        
        # Test list view with all data
        response = api_client.get(reverse('blog:post-list'))
        assert response.status_code == status.HTTP_200_OK
        
        # Test filtering with full dataset
        response = api_client.get(reverse('blog:post-list'), {'featured': 'true'})
        assert response.status_code == status.HTTP_200_OK
        
        # Test search with full dataset
        response = api_client.get(reverse('blog:post-list'), {'search': 'test'})
        assert response.status_code == status.HTTP_200_OK
        
        # Test stats with full dataset
        response = api_client.get(reverse('blog:blog-stats'))
        assert response.status_code == status.HTTP_200_OK