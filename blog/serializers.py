from rest_framework import serializers
from django.contrib.auth.models import User
from .models import BlogPost, Category, Tag, Comment


class UserSerializer(serializers.ModelSerializer):
    """Serializer for User model"""
    
    class Meta:
        model = User
        fields = ['id', 'username', 'first_name', 'last_name']


class CategorySerializer(serializers.ModelSerializer):
    """Serializer for Category model"""
    posts_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'posts_count', 'created_at']
    
    def get_posts_count(self, obj):
        return obj.posts.filter(status='published').count()


class TagSerializer(serializers.ModelSerializer):
    """Serializer for Tag model"""
    posts_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Tag
        fields = ['id', 'name', 'slug', 'posts_count', 'created_at']
    
    def get_posts_count(self, obj):
        return obj.posts.filter(status='published').count()


class CommentSerializer(serializers.ModelSerializer):
    """Serializer for Comment model"""
    
    class Meta:
        model = Comment
        fields = ['id', 'name', 'email', 'content', 'created_at']
        extra_kwargs = {
            'email': {'write_only': True}
        }


class BlogPostSerializer(serializers.ModelSerializer):
    """Detailed serializer for BlogPost model"""
    author = UserSerializer(read_only=True)
    category = CategorySerializer(read_only=True)
    tags = TagSerializer(many=True, read_only=True)
    comments = CommentSerializer(many=True, read_only=True)
    comments_count = serializers.SerializerMethodField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'slug', 'excerpt', 'content', 'author', 'category',
            'tags', 'featured_image', 'status', 'status_display', 'featured',
            'read_time', 'views', 'comments', 'comments_count', 'created_at',
            'updated_at', 'published_at'
        ]
    
    def get_comments_count(self, obj):
        return obj.comments.filter(approved=True).count()


class BlogPostListSerializer(serializers.ModelSerializer):
    """Simplified serializer for blog post list view"""
    author = serializers.StringRelatedField(read_only=True)
    category = serializers.StringRelatedField(read_only=True)
    tags = serializers.StringRelatedField(many=True, read_only=True)
    comments_count = serializers.SerializerMethodField()
    
    class Meta:
        model = BlogPost
        fields = [
            'id', 'title', 'slug', 'excerpt', 'author', 'category', 'tags',
            'featured_image', 'featured', 'read_time', 'views', 'comments_count',
            'created_at', 'published_at'
        ]
    
    def get_comments_count(self, obj):
        return obj.comments.filter(approved=True).count()