"""
Comprehensive pytest tests for blog application models.

This module provides thorough testing for all blog models including:
- Category model: creation, slug generation, string representation
- Tag model: creation, slug generation, string representation  
- BlogPost model: creation, slug generation, publishing workflow, relationships
- Comment model: creation, approval workflow, relationships

Tests cover:
- Model field validation and constraints
- Automatic slug generation from names/titles
- Model relationships (ForeignKey, ManyToMany)
- Custom model methods and properties
- String representations
- Model ordering and meta options
"""

import pytest
from django.test import TestCase
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from django.utils import timezone
from datetime import datetime, timedelta
from blog.models import Category, Tag, BlogPost, Comment


@pytest.mark.django_db
class TestCategoryModel:
    """Test cases for the Category model."""
    
    def test_category_creation(self):
        """Test basic category creation with all fields."""
        category = Category.objects.create(
            name="Technology",
            description="Tech-related posts"
        )
        
        assert category.name == "Technology"
        assert category.slug == "technology"  # Auto-generated
        assert category.description == "Tech-related posts"
        assert category.created_at is not None
        assert isinstance(category.created_at, datetime)
    
    def test_category_slug_auto_generation(self):
        """Test automatic slug generation from category name."""
        category = Category.objects.create(name="Web Development")
        assert category.slug == "web-development"
        
        # Test with special characters
        category2 = Category.objects.create(name="AI & Machine Learning")
        assert category2.slug == "ai-machine-learning"
    
    def test_category_custom_slug(self):
        """Test category creation with custom slug."""
        category = Category.objects.create(
            name="Technology",
            slug="custom-tech-slug"
        )
        assert category.slug == "custom-tech-slug"
    
    def test_category_unique_name_constraint(self):
        """Test that category names must be unique."""
        Category.objects.create(name="Technology")
        
        with pytest.raises(IntegrityError):
            Category.objects.create(name="Technology")
    
    def test_category_unique_slug_constraint(self):
        """Test that category slugs must be unique."""
        Category.objects.create(name="Technology", slug="tech")
        
        with pytest.raises(IntegrityError):
            Category.objects.create(name="Tech", slug="tech")
    
    def test_category_string_representation(self):
        """Test category string representation."""
        category = Category.objects.create(name="Technology")
        assert str(category) == "Technology"
    
    def test_category_ordering(self):
        """Test category ordering by name."""
        Category.objects.create(name="Zebra")
        Category.objects.create(name="Alpha")
        Category.objects.create(name="Beta")
        
        categories = list(Category.objects.all())
        assert categories[0].name == "Alpha"
        assert categories[1].name == "Beta"
        assert categories[2].name == "Zebra"
    
    def test_category_blank_description(self):
        """Test category creation with blank description."""
        category = Category.objects.create(name="Technology")
        assert category.description == ""


@pytest.mark.django_db
class TestTagModel:
    """Test cases for the Tag model."""
    
    def test_tag_creation(self):
        """Test basic tag creation."""
        tag = Tag.objects.create(name="Python")
        
        assert tag.name == "Python"
        assert tag.slug == "python"  # Auto-generated
        assert tag.created_at is not None
        assert isinstance(tag.created_at, datetime)
    
    def test_tag_slug_auto_generation(self):
        """Test automatic slug generation from tag name."""
        tag = Tag.objects.create(name="Machine Learning")
        assert tag.slug == "machine-learning"
        
        # Test with special characters
        tag2 = Tag.objects.create(name="C++")
        assert tag2.slug == "c"
    
    def test_tag_custom_slug(self):
        """Test tag creation with custom slug."""
        tag = Tag.objects.create(name="Python", slug="python-lang")
        assert tag.slug == "python-lang"
    
    def test_tag_unique_name_constraint(self):
        """Test that tag names must be unique."""
        Tag.objects.create(name="Python")
        
        with pytest.raises(IntegrityError):
            Tag.objects.create(name="Python")
    
    def test_tag_unique_slug_constraint(self):
        """Test that tag slugs must be unique."""
        Tag.objects.create(name="Python", slug="py")
        
        with pytest.raises(IntegrityError):
            Tag.objects.create(name="Py", slug="py")
    
    def test_tag_string_representation(self):
        """Test tag string representation."""
        tag = Tag.objects.create(name="Django")
        assert str(tag) == "Django"
    
    def test_tag_ordering(self):
        """Test tag ordering by name."""
        Tag.objects.create(name="Zebra")
        Tag.objects.create(name="Alpha")
        Tag.objects.create(name="Beta")
        
        tags = list(Tag.objects.all())
        assert tags[0].name == "Alpha"
        assert tags[1].name == "Beta"
        assert tags[2].name == "Zebra"


@pytest.mark.django_db
class TestBlogPostModel:
    """Test cases for the BlogPost model."""
    
    @pytest.fixture
    def user(self):
        """Create a test user."""
        return User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
    
    @pytest.fixture
    def category(self):
        """Create a test category."""
        return Category.objects.create(name="Technology")
    
    @pytest.fixture
    def tags(self):
        """Create test tags."""
        return [
            Tag.objects.create(name="Python"),
            Tag.objects.create(name="Django")
        ]
    
    def test_blog_post_creation(self, user, category):
        """Test basic blog post creation."""
        post = BlogPost.objects.create(
            title="My First Post",
            excerpt="This is a test post",
            content="Full content of the post",
            author=user,
            category=category,
            status="published"
        )
        
        assert post.title == "My First Post"
        assert post.slug == "my-first-post"  # Auto-generated
        assert post.excerpt == "This is a test post"
        assert post.content == "Full content of the post"
        assert post.author == user
        assert post.category == category
        assert post.status == "published"
        assert post.featured is False  # Default
        assert post.read_time == 5  # Default
        assert post.views == 0  # Default
        assert post.created_at is not None
        assert post.updated_at is not None
    
    def test_blog_post_slug_auto_generation(self, user):
        """Test automatic slug generation from title."""
        post = BlogPost.objects.create(
            title="How to Learn Python Programming",
            content="Content here",
            author=user
        )
        assert post.slug == "how-to-learn-python-programming"
    
    def test_blog_post_custom_slug(self, user):
        """Test blog post creation with custom slug."""
        post = BlogPost.objects.create(
            title="My Post",
            slug="custom-post-slug",
            content="Content here",
            author=user
        )
        assert post.slug == "custom-post-slug"
    
    def test_blog_post_unique_slug_constraint(self, user):
        """Test that blog post slugs must be unique."""
        BlogPost.objects.create(
            title="First Post",
            slug="test-post",
            content="Content",
            author=user
        )
        
        with pytest.raises(IntegrityError):
            BlogPost.objects.create(
                title="Second Post",
                slug="test-post",
                content="Content",
                author=user
            )
    
    def test_blog_post_published_at_auto_set(self, user):
        """Test that published_at is set when status changes to published."""
        post = BlogPost.objects.create(
            title="Draft Post",
            content="Content",
            author=user,
            status="draft"
        )
        assert post.published_at is None
        
        # Change to published
        post.status = "published"
        post.save()
        assert post.published_at is not None
        assert isinstance(post.published_at, datetime)
    
    def test_blog_post_published_at_not_overwritten(self, user):
        """Test that published_at is not overwritten on subsequent saves."""
        post = BlogPost.objects.create(
            title="Published Post",
            content="Content",
            author=user,
            status="published"
        )
        original_published_at = post.published_at
        
        # Save again
        post.save()
        assert post.published_at == original_published_at
    
    def test_blog_post_is_published_property(self, user):
        """Test the is_published property."""
        draft_post = BlogPost.objects.create(
            title="Draft",
            content="Content",
            author=user,
            status="draft"
        )
        assert draft_post.is_published is False
        
        published_post = BlogPost.objects.create(
            title="Published",
            content="Content",
            author=user,
            status="published"
        )
        assert published_post.is_published is True
        
        archived_post = BlogPost.objects.create(
            title="Archived",
            content="Content",
            author=user,
            status="archived"
        )
        assert archived_post.is_published is False
    
    def test_blog_post_tags_relationship(self, user, tags):
        """Test many-to-many relationship with tags."""
        post = BlogPost.objects.create(
            title="Tagged Post",
            content="Content",
            author=user
        )
        
        # Add tags
        post.tags.add(*tags)
        
        assert post.tags.count() == 2
        assert tags[0] in post.tags.all()
        assert tags[1] in post.tags.all()
    
    def test_blog_post_category_null_allowed(self, user):
        """Test that category can be null."""
        post = BlogPost.objects.create(
            title="Uncategorized Post",
            content="Content",
            author=user,
            category=None
        )
        assert post.category is None
    
    def test_blog_post_string_representation(self, user):
        """Test blog post string representation."""
        post = BlogPost.objects.create(
            title="My Amazing Post",
            content="Content",
            author=user
        )
        assert str(post) == "My Amazing Post"
    
    def test_blog_post_ordering(self, user):
        """Test blog post ordering by published_at and created_at."""
        # Create posts with different timestamps
        old_post = BlogPost.objects.create(
            title="Old Post",
            content="Content",
            author=user,
            status="published"
        )
        old_post.published_at = timezone.now() - timedelta(days=2)
        old_post.save()
        
        new_post = BlogPost.objects.create(
            title="New Post",
            content="Content",
            author=user,
            status="published"
        )
        
        posts = list(BlogPost.objects.all())
        assert posts[0] == new_post  # Newer first
        assert posts[1] == old_post


@pytest.mark.django_db
class TestCommentModel:
    """Test cases for the Comment model."""
    
    @pytest.fixture
    def user(self):
        """Create a test user."""
        return User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )
    
    @pytest.fixture
    def blog_post(self, user):
        """Create a test blog post."""
        return BlogPost.objects.create(
            title="Test Post",
            content="Test content",
            author=user,
            status="published"
        )
    
    def test_comment_creation(self, blog_post):
        """Test basic comment creation."""
        comment = Comment.objects.create(
            post=blog_post,
            name="John Doe",
            email="john@example.com",
            content="Great post!"
        )
        
        assert comment.post == blog_post
        assert comment.name == "John Doe"
        assert comment.email == "john@example.com"
        assert comment.content == "Great post!"
        assert comment.approved is False  # Default
        assert comment.created_at is not None
        assert isinstance(comment.created_at, datetime)
    
    def test_comment_approved_default(self, blog_post):
        """Test that comments are not approved by default."""
        comment = Comment.objects.create(
            post=blog_post,
            name="Jane Doe",
            email="jane@example.com",
            content="Nice article!"
        )
        assert comment.approved is False
    
    def test_comment_string_representation(self, blog_post):
        """Test comment string representation."""
        comment = Comment.objects.create(
            post=blog_post,
            name="Alice Smith",
            email="alice@example.com",
            content="Interesting read!"
        )
        expected = f"Comment by Alice Smith on {blog_post.title}"
        assert str(comment) == expected
    
    def test_comment_ordering(self, blog_post):
        """Test comment ordering by created_at (newest first)."""
        # Create comments with small delay
        import time
        
        old_comment = Comment.objects.create(
            post=blog_post,
            name="First",
            email="first@example.com",
            content="First comment"
        )
        
        time.sleep(0.01)  # Small delay
        
        new_comment = Comment.objects.create(
            post=blog_post,
            name="Second",
            email="second@example.com",
            content="Second comment"
        )
        
        comments = list(Comment.objects.all())
        assert comments[0] == new_comment  # Newer first
        assert comments[1] == old_comment
    
    def test_comment_post_relationship(self, blog_post):
        """Test relationship between comment and blog post."""
        comment = Comment.objects.create(
            post=blog_post,
            name="Commenter",
            email="commenter@example.com",
            content="Test comment"
        )
        
        # Test forward relationship
        assert comment.post == blog_post
        
        # Test reverse relationship
        assert comment in blog_post.comments.all()
        assert blog_post.comments.count() == 1