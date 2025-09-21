"""
Comprehensive pytest tests for blog application serializers.

This module provides thorough testing for all blog DRF serializers including:
- CategorySerializer: category data serialization and validation
- TagSerializer: tag data serialization and validation  
- BlogPostSerializer: blog post serialization with nested relationships
- CommentSerializer: comment serialization and validation

Tests cover:
- Serialization of model instances to JSON
- Deserialization and validation of input data
- Field validation and constraints
- Nested serializer relationships
- Read-only and write-only fields
- Custom validation methods
- Error handling and validation messages
"""

import pytest
from django.test import TestCase
from django.contrib.auth.models import User
from rest_framework.test import APIRequestFactory
from rest_framework import serializers
from blog.models import Category, Tag, BlogPost, Comment
from blog.serializers import CategorySerializer, TagSerializer, BlogPostSerializer, CommentSerializer
from datetime import datetime


@pytest.mark.django_db
class TestCategorySerializer:
    """Test cases for the CategorySerializer."""
    
    @pytest.fixture
    def category_data(self):
        """Sample category data for testing."""
        return {
            'name': 'Technology',
            'description': 'Technology related posts'
        }
    
    def test_category_serialization(self):
        """Test serializing a category instance."""
        category = Category.objects.create(
            name='Programming',
            description='Programming tutorials and tips'
        )
        
        serializer = CategorySerializer(category)
        data = serializer.data
        
        assert data['id'] == category.id
        assert data['name'] == 'Programming'
        assert data['slug'] == 'programming'
        assert data['description'] == 'Programming tutorials and tips'
        assert 'created_at' in data
    
    def test_category_deserialization_valid(self, category_data):
        """Test deserializing valid category data."""
        serializer = CategorySerializer(data=category_data)
        
        assert serializer.is_valid()
        category = serializer.save()
        
        assert category.name == 'Technology'
        assert category.slug == 'technology'
        assert category.description == 'Technology related posts'
    
    def test_category_deserialization_invalid_name(self):
        """Test deserializing category with invalid name."""
        invalid_data = {
            'name': '',  # Empty name should be invalid
            'description': 'Test description'
        }
        
        serializer = CategorySerializer(data=invalid_data)
        assert not serializer.is_valid()
        assert 'name' in serializer.errors
    
    def test_category_update(self):
        """Test updating a category through serializer."""
        category = Category.objects.create(
            name='Old Name',
            description='Old description'
        )
        
        update_data = {
            'name': 'New Name',
            'description': 'New description'
        }
        
        serializer = CategorySerializer(category, data=update_data)
        assert serializer.is_valid()
        
        updated_category = serializer.save()
        assert updated_category.name == 'New Name'
        assert updated_category.slug == 'new-name'
        assert updated_category.description == 'New description'


@pytest.mark.django_db
class TestTagSerializer:
    """Test cases for the TagSerializer."""
    
    @pytest.fixture
    def tag_data(self):
        """Sample tag data for testing."""
        return {
            'name': 'Python'
        }
    
    def test_tag_serialization(self):
        """Test serializing a tag instance."""
        tag = Tag.objects.create(name='Django')
        
        serializer = TagSerializer(tag)
        data = serializer.data
        
        assert data['id'] == tag.id
        assert data['name'] == 'Django'
        assert data['slug'] == 'django'
        assert 'created_at' in data
    
    def test_tag_deserialization_valid(self, tag_data):
        """Test deserializing valid tag data."""
        serializer = TagSerializer(data=tag_data)
        
        assert serializer.is_valid()
        tag = serializer.save()
        
        assert tag.name == 'Python'
        assert tag.slug == 'python'
    
    def test_tag_deserialization_invalid_name(self):
        """Test deserializing tag with invalid name."""
        invalid_data = {
            'name': ''  # Empty name should be invalid
        }
        
        serializer = TagSerializer(data=invalid_data)
        assert not serializer.is_valid()
        assert 'name' in serializer.errors
    
    def test_tag_unique_name_validation(self):
        """Test that tag names must be unique."""
        # Create existing tag
        Tag.objects.create(name='Existing Tag')
        
        # Try to create another tag with same name
        duplicate_data = {'name': 'Existing Tag'}
        serializer = TagSerializer(data=duplicate_data)
        
        assert not serializer.is_valid()
        assert 'name' in serializer.errors


@pytest.mark.django_db
class TestBlogPostSerializer:
    """Test cases for the BlogPostSerializer."""
    
    @pytest.fixture
    def user(self):
        """Create a test user."""
        return User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    @pytest.fixture
    def category(self):
        """Create a test category."""
        return Category.objects.create(
            name='Test Category',
            description='Test category description'
        )
    
    @pytest.fixture
    def tags(self):
        """Create test tags."""
        return [
            Tag.objects.create(name='Python'),
            Tag.objects.create(name='Django')
        ]
    
    @pytest.fixture
    def blog_post_data(self, user, category, tags):
        """Sample blog post data for testing."""
        return {
            'title': 'Test Blog Post',
            'excerpt': 'This is a test excerpt',
            'content': 'This is the full content of the test blog post.',
            'author_id': user.id,
            'category_id': category.id,
            'tag_ids': [tag.id for tag in tags],
            'status': 'published',
            'featured': True
        }
    
    def test_blog_post_serialization(self, user, category, tags):
        """Test serializing a blog post instance."""
        blog_post = BlogPost.objects.create(
            title='Sample Post',
            excerpt='Sample excerpt',
            content='Sample content',
            author=user,
            category=category,
            status='published'
        )
        blog_post.tags.set(tags)
        
        serializer = BlogPostSerializer(blog_post)
        data = serializer.data
        
        assert data['id'] == blog_post.id
        assert data['title'] == 'Sample Post'
        assert data['slug'] == 'sample-post'
        assert data['excerpt'] == 'Sample excerpt'
        assert data['content'] == 'Sample content'
        assert data['author']['id'] == user.id
        assert data['author']['username'] == user.username
        assert data['category']['id'] == category.id
        assert data['category']['name'] == category.name
        assert len(data['tags']) == 2
        assert data['status'] == 'published'
        assert 'created_at' in data
        assert 'updated_at' in data
    
    def test_blog_post_deserialization_valid(self, blog_post_data):
        """Test deserializing valid blog post data."""
        serializer = BlogPostSerializer(data=blog_post_data)
        
        assert serializer.is_valid(), serializer.errors
        blog_post = serializer.save()
        
        assert blog_post.title == 'Test Blog Post'
        assert blog_post.slug == 'test-blog-post'
        assert blog_post.excerpt == 'This is a test excerpt'
        assert blog_post.content == 'This is the full content of the test blog post.'
        assert blog_post.status == 'published'
        assert blog_post.featured is True
        assert blog_post.tags.count() == 2
    
    def test_blog_post_deserialization_invalid_title(self, blog_post_data):
        """Test deserializing blog post with invalid title."""
        blog_post_data['title'] = ''  # Empty title
        
        serializer = BlogPostSerializer(data=blog_post_data)
        assert not serializer.is_valid()
        assert 'title' in serializer.errors
    
    def test_blog_post_deserialization_invalid_author(self, blog_post_data):
        """Test deserializing blog post with invalid author."""
        blog_post_data['author_id'] = 99999  # Non-existent user ID
        
        serializer = BlogPostSerializer(data=blog_post_data)
        assert not serializer.is_valid()
        assert 'author_id' in serializer.errors
    
    def test_blog_post_deserialization_invalid_category(self, blog_post_data):
        """Test deserializing blog post with invalid category."""
        blog_post_data['category_id'] = 99999  # Non-existent category ID
        
        serializer = BlogPostSerializer(data=blog_post_data)
        assert not serializer.is_valid()
        assert 'category_id' in serializer.errors
    
    def test_blog_post_status_choices_validation(self, blog_post_data):
        """Test blog post status choices validation."""
        # Valid status
        blog_post_data['status'] = 'draft'
        serializer = BlogPostSerializer(data=blog_post_data)
        assert serializer.is_valid()
        
        # Invalid status
        blog_post_data['status'] = 'invalid_status'
        serializer = BlogPostSerializer(data=blog_post_data)
        assert not serializer.is_valid()
        assert 'status' in serializer.errors
    
    def test_blog_post_nested_serializers(self, user, category, tags):
        """Test nested serializers for author, category, and tags."""
        blog_post = BlogPost.objects.create(
            title='Nested Test',
            content='Testing nested serializers',
            author=user,
            category=category
        )
        blog_post.tags.set(tags)
        
        serializer = BlogPostSerializer(blog_post)
        data = serializer.data
        
        # Check nested author data
        assert 'author' in data
        assert data['author']['username'] == user.username
        assert data['author']['email'] == user.email
        
        # Check nested category data
        assert 'category' in data
        assert data['category']['name'] == category.name
        assert data['category']['slug'] == category.slug
        
        # Check nested tags data
        assert 'tags' in data
        assert len(data['tags']) == 2
        for tag_data in data['tags']:
            assert 'name' in tag_data
            assert 'slug' in tag_data
    
    def test_blog_post_update(self, user, category, tags):
        """Test updating a blog post through serializer."""
        blog_post = BlogPost.objects.create(
            title='Original Title',
            content='Original content',
            author=user,
            category=category,
            status='draft'
        )
        
        update_data = {
            'title': 'Updated Title',
            'content': 'Updated content',
            'status': 'published',
            'featured': True
        }
        
        serializer = BlogPostSerializer(blog_post, data=update_data, partial=True)
        assert serializer.is_valid()
        
        updated_post = serializer.save()
        assert updated_post.title == 'Updated Title'
        assert updated_post.slug == 'updated-title'
        assert updated_post.content == 'Updated content'
        assert updated_post.status == 'published'
        assert updated_post.featured is True


@pytest.mark.django_db
class TestCommentSerializer:
    """Test cases for the CommentSerializer."""
    
    @pytest.fixture
    def user(self):
        """Create a test user."""
        return User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
    
    @pytest.fixture
    def category(self):
        """Create a test category."""
        return Category.objects.create(name='Test Category')
    
    @pytest.fixture
    def blog_post(self, user, category):
        """Create a test blog post."""
        return BlogPost.objects.create(
            title='Test Post',
            content='Test content',
            author=user,
            category=category,
            status='published'
        )
    
    @pytest.fixture
    def comment_data(self, blog_post):
        """Sample comment data for testing."""
        return {
            'post': blog_post.id,
            'name': 'John Commenter',
            'email': 'john@example.com',
            'content': 'This is a test comment.'
        }
    
    def test_comment_serialization(self, blog_post):
        """Test serializing a comment instance."""
        comment = Comment.objects.create(
            post=blog_post,
            name='Jane Doe',
            email='jane@example.com',
            content='Great post!',
            approved=True
        )
        
        serializer = CommentSerializer(comment)
        data = serializer.data
        
        assert data['id'] == comment.id
        assert data['post'] == blog_post.id
        assert data['name'] == 'Jane Doe'
        assert data['email'] == 'jane@example.com'
        assert data['content'] == 'Great post!'
        assert data['approved'] is True
        assert 'created_at' in data
    
    def test_comment_deserialization_valid(self, comment_data):
        """Test deserializing valid comment data."""
        serializer = CommentSerializer(data=comment_data)
        
        assert serializer.is_valid(), serializer.errors
        comment = serializer.save()
        
        assert comment.name == 'John Commenter'
        assert comment.email == 'john@example.com'
        assert comment.content == 'This is a test comment.'
        assert comment.approved is False  # Default value
    
    def test_comment_deserialization_invalid_name(self, comment_data):
        """Test deserializing comment with invalid name."""
        comment_data['name'] = ''  # Empty name
        
        serializer = CommentSerializer(data=comment_data)
        assert not serializer.is_valid()
        assert 'name' in serializer.errors
    
    def test_comment_deserialization_invalid_email(self, comment_data):
        """Test deserializing comment with invalid email."""
        comment_data['email'] = 'invalid-email'  # Invalid email format
        
        serializer = CommentSerializer(data=comment_data)
        assert not serializer.is_valid()
        assert 'email' in serializer.errors
    
    def test_comment_deserialization_invalid_post(self, comment_data):
        """Test deserializing comment with invalid post."""
        comment_data['post'] = 99999  # Non-existent post ID
        
        serializer = CommentSerializer(data=comment_data)
        assert not serializer.is_valid()
        assert 'post' in serializer.errors
    
    def test_comment_deserialization_empty_content(self, comment_data):
        """Test deserializing comment with empty content."""
        comment_data['content'] = ''  # Empty content
        
        serializer = CommentSerializer(data=comment_data)
        assert not serializer.is_valid()
        assert 'content' in serializer.errors
    
    def test_comment_approved_default_value(self, comment_data):
        """Test that comments are not approved by default."""
        serializer = CommentSerializer(data=comment_data)
        assert serializer.is_valid()
        
        comment = serializer.save()
        assert comment.approved is False
    
    def test_comment_update(self, blog_post):
        """Test updating a comment through serializer."""
        comment = Comment.objects.create(
            post=blog_post,
            name='Original Name',
            email='original@example.com',
            content='Original content',
            approved=False
        )
        
        update_data = {
            'name': 'Updated Name',
            'email': 'updated@example.com',
            'content': 'Updated content',
            'approved': True
        }
        
        serializer = CommentSerializer(comment, data=update_data, partial=True)
        assert serializer.is_valid()
        
        updated_comment = serializer.save()
        assert updated_comment.name == 'Updated Name'
        assert updated_comment.email == 'updated@example.com'
        assert updated_comment.content == 'Updated content'
        assert updated_comment.approved is True


@pytest.mark.django_db
class TestSerializerIntegration:
    """Integration tests for blog serializers working together."""
    
    @pytest.fixture
    def complete_blog_setup(self):
        """Create complete blog setup with all related objects."""
        user = User.objects.create_user(
            username='bloguser',
            email='blog@example.com',
            password='blogpass123'
        )
        
        category = Category.objects.create(
            name='Web Development',
            description='Web development tutorials'
        )
        
        tags = [
            Tag.objects.create(name='Python'),
            Tag.objects.create(name='Django'),
            Tag.objects.create(name='REST API')
        ]
        
        blog_post = BlogPost.objects.create(
            title='Building REST APIs with Django',
            excerpt='Learn how to build REST APIs',
            content='Detailed content about building REST APIs with Django...',
            author=user,
            category=category,
            status='published',
            featured=True
        )
        blog_post.tags.set(tags)
        
        comments = [
            Comment.objects.create(
                post=blog_post,
                name='Alice Reader',
                email='alice@example.com',
                content='Great tutorial!',
                approved=True
            ),
            Comment.objects.create(
                post=blog_post,
                name='Bob Developer',
                email='bob@example.com',
                content='Very helpful, thanks!',
                approved=True
            )
        ]
        
        return {
            'user': user,
            'category': category,
            'tags': tags,
            'blog_post': blog_post,
            'comments': comments
        }
    
    def test_complete_blog_post_serialization(self, complete_blog_setup):
        """Test serializing a complete blog post with all relationships."""
        blog_post = complete_blog_setup['blog_post']
        
        serializer = BlogPostSerializer(blog_post)
        data = serializer.data
        
        # Verify all nested data is present
        assert 'author' in data
        assert 'category' in data
        assert 'tags' in data
        assert len(data['tags']) == 3
        
        # Verify nested data structure
        assert data['author']['username'] == 'bloguser'
        assert data['category']['name'] == 'Web Development'
        
        tag_names = [tag['name'] for tag in data['tags']]
        assert 'Python' in tag_names
        assert 'Django' in tag_names
        assert 'REST API' in tag_names
    
    def test_serializer_validation_chain(self, complete_blog_setup):
        """Test validation across related serializers."""
        category = complete_blog_setup['category']
        user = complete_blog_setup['user']
        
        # Test creating blog post with existing category and new tags
        blog_data = {
            'title': 'Another Great Post',
            'content': 'More great content',
            'author': user.id,
            'category': category.id,
            'tags': [],  # No tags
            'status': 'draft'
        }
        
        serializer = BlogPostSerializer(data=blog_data)
        assert serializer.is_valid()
        
        new_post = serializer.save()
        assert new_post.title == 'Another Great Post'
        assert new_post.category == category
        assert new_post.author == user
        assert new_post.tags.count() == 0