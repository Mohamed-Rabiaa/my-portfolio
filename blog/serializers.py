"""
Blog application serializers for REST API data transformation.

This module provides serializers for converting Django model instances to/from
JSON format for the blog API endpoints. Includes serializers for:
- Blog posts (detailed and list views)
- Categories and tags
- Comments and user information
- Custom field calculations and data formatting
"""

from rest_framework import serializers
from django.contrib.auth.models import User
from .models import BlogPost, Category, Tag, Comment
from common.validators import (
    ValidationMixin, validate_safe_html, validate_clean_text, 
    validate_no_sql_injection, InputSanitizer
)


class UserSerializer(serializers.ModelSerializer):
    """
    Serializer for User model in blog context.
    
    Provides essential user information for blog post authorship display
    including email for nested serialization within blog post data.
    
    Fields:
        - id: Unique user identifier
        - username: User's login name
        - first_name: User's first name
        - last_name: User's last name
        - email: User's email address
    """
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name', 'email']


class CategorySerializer(serializers.ModelSerializer):
    """
    Serializer for blog Category model with post count statistics.
    
    Transforms category data for API consumption, including a calculated
    field showing the number of published posts in each category. This
    helps with navigation and content organization displays.
    
    Fields:
        - id: Unique category identifier
        - name: Category display name
        - slug: URL-friendly category identifier
        - description: Category description text
        - posts_count: Number of published posts (calculated)
        - created_at: Category creation timestamp
    """
    posts_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'posts_count', 'created_at']
    
    def get_posts_count(self, obj):
        """
        Calculate the number of published posts in this category.
        
        Args:
            obj: Category model instance
            
        Returns:
            int: Count of published posts in this category
        """
        return obj.posts.filter(status='published').count()


class TagSerializer(serializers.ModelSerializer):
    """
    Serializer for blog Tag model with usage statistics.
    
    Transforms tag data for API consumption, including a calculated field
    showing how many published posts use each tag. This information is
    useful for tag clouds and content discovery features.
    
    Fields:
        - id: Unique tag identifier
        - name: Tag display name
        - slug: URL-friendly tag identifier
        - posts_count: Number of published posts using this tag (calculated)
        - created_at: Tag creation timestamp
    """
    posts_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug', 'posts_count', 'created_at']
    
    def get_posts_count(self, obj):
        """
        Calculate the number of published posts using this tag.
        
        Args:
            obj: Tag model instance
            
        Returns:
            int: Count of published posts tagged with this tag
        """
        return obj.posts.filter(status='published').count()


class CommentSerializer(ValidationMixin, serializers.ModelSerializer):
    """
    Serializer for blog Comment model with privacy protection.
    
    Handles comment data transformation for both reading and writing operations.
    Email addresses are write-only to protect commenter privacy while still
    allowing notification functionality. Comments require moderation approval
    before public display.
    
    Fields:
        - id: Unique comment identifier
        - post_id: Blog post ID (write-only for creating comments)
        - name: Commenter's display name
        - email: Commenter's email (write-only for privacy)
        - content: Comment text content
        - created_at: Comment submission timestamp
    """
    post_id = serializers.PrimaryKeyRelatedField(
        queryset=BlogPost.objects.all(),
        source='post',
        write_only=True
    )
    
    class Meta:
        model = Comment
        fields = ['id', 'post_id', 'name', 'email', 'content', 'created_at']
        extra_kwargs = {
            'email': {'write_only': True}
        }
    
    def validate_name(self, value):
        """Validate and sanitize commenter name."""
        return validate_clean_text(value, max_length=100)
    
    def validate_email(self, value):
        """Validate commenter email address."""
        return self.validate_email_field(value)
    
    def validate_content(self, value):
        """Validate and sanitize comment content."""
        # Allow basic HTML but sanitize dangerous content
        return validate_safe_html(value, max_length=2000)


class BlogPostSerializer(ValidationMixin, serializers.ModelSerializer):
    """
    Comprehensive serializer for detailed BlogPost model representation.
    
    Provides complete blog post data including all related information such as
    author details, category, tags, and comments. Used for single post views
    where full content and metadata are needed. Includes calculated fields
    for enhanced functionality.
    
    Features:
        - Nested author information (read-only for output, validated for input)
        - Full category and tag details (read-only)
        - Associated approved comments (read-only)
        - Comment count calculation
        - Human-readable status display
        - Complete post metadata and content
    
    Fields include all BlogPost model fields plus calculated and nested data.
    """
    author = UserSerializer(read_only=True)
    author_id = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), 
        source='author', 
        write_only=True,
        required=False
    )
    category = CategorySerializer(read_only=True)
    category_id = serializers.PrimaryKeyRelatedField(
        queryset=Category.objects.all(),
        source='category',
        write_only=True,
        required=False
    )
    tags = TagSerializer(many=True, read_only=True)
    tag_ids = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(),
        source='tags',
        many=True,
        write_only=True,
        required=False
    )
    comments = CommentSerializer(many=True, read_only=True)
    comments_count = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'slug', 'excerpt', 'content', 'author', 'author_id',
            'category', 'category_id', 'tags', 'tag_ids', 'featured_image', 
            'status', 'status_display', 'featured', 'read_time', 'views', 
            'comments', 'comments_count', 'created_at', 'updated_at', 'published_at'
        ]
    
    def get_comments_count(self, obj):
        """
        Calculate the number of approved comments for this post.
        
        Args:
            obj: BlogPost model instance
            
        Returns:
            int: Count of approved comments on this post
        """
        return obj.comments.filter(approved=True).count()
    
    def validate_title(self, value):
        """Validate and sanitize blog post title."""
        return validate_clean_text(value, max_length=200)
    
    def validate_excerpt(self, value):
        """Validate and sanitize blog post excerpt."""
        if value:
            return validate_clean_text(value, max_length=500)
        return value
    
    def validate_content(self, value):
        """Validate and sanitize blog post content."""
        # Allow rich HTML content but sanitize dangerous elements
        return validate_safe_html(value, max_length=50000)


class BlogPostListSerializer(serializers.ModelSerializer):
    """
    Optimized serializer for BlogPost model in list views.
    
    Provides essential blog post information for list displays with minimal
    data transfer. Uses string representations for related objects instead
    of full nested serialization to improve performance. Ideal for blog
    post listings, search results, and archive pages.
    
    Features:
        - Lightweight data representation
        - String-based related object display
        - Essential metadata only
        - Optimized for list performance
        - Comment count calculation
    
    Fields include core BlogPost information without full content or
    detailed nested relationships.
    """
    author = serializers.StringRelatedField(read_only=True)
    category = serializers.StringRelatedField(read_only=True)
    tags = serializers.StringRelatedField(many=True, read_only=True)
    comments_count = serializers.SerializerMethodField()
    
    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'slug', 'excerpt', 'content', 'author', 'category', 'tags',
            'featured_image', 'featured', 'read_time', 'views', 'comments_count',
            'created_at', 'published_at'
        ]
    
    def get_comments_count(self, obj):
        """
        Calculate the number of approved comments for this post.
        
        Args:
            obj: BlogPost model instance
            
        Returns:
            int: Count of approved comments on this post
        """
        return obj.comments.filter(approved=True).count()