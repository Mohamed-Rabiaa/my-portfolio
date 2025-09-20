"""
Blog application views for handling blog post, category, tag, and comment operations.

This module provides REST API views for the blog functionality including:
- Blog post listing, detail viewing, and filtering
- Category and tag management
- Comment creation and moderation
- Blog statistics and analytics
- Featured and popular post endpoints
"""

from rest_framework import generics, filters, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import F
from .models import BlogPost, Category, Tag, Comment
from .serializers import (
    BlogPostSerializer, BlogPostListSerializer, CategorySerializer,
    TagSerializer, CommentSerializer
)

class BlogPostListView(generics.ListAPIView):
    """
    API view to list all published blog posts with advanced filtering capabilities.
    
    Provides comprehensive blog post listing with support for:
    - Filtering by category, tags, featured status, and author
    - Full-text search across title, excerpt, content, and tag names
    - Ordering by publication date, view count, or title
    - Pagination for large result sets
    
    Only returns posts with 'published' status to ensure content quality.
    """
    queryset = BlogPost.objects.filter(status='published')
    serializer_class = BlogPostListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'tags', 'featured', 'author']
    search_fields = ['title', 'excerpt', 'content', 'tags__name']
    ordering_fields = ['published_at', 'views', 'title']
    ordering = ['-published_at']


class BlogPostDetailView(generics.RetrieveAPIView):
    """
    API view to retrieve a single blog post by its slug with view tracking.
    
    Features:
    - Fetches blog post using SEO-friendly slug instead of ID
    - Automatically increments view count for analytics
    - Returns full post content including related data
    - Only serves published posts to maintain content control
    
    The view count is atomically incremented to prevent race conditions
    in high-traffic scenarios.
    """
    queryset = BlogPost.objects.filter(status='published')
    serializer_class = BlogPostSerializer
    lookup_field = 'slug'

    def retrieve(self, request, *args, **kwargs):
        """
        Override retrieve method to increment view count.
        
        Args:
            request: HTTP request object
            *args: Variable length argument list
            **kwargs: Arbitrary keyword arguments
            
        Returns:
            Response: Serialized blog post data with updated view count
        """
        instance = self.get_object()
        # Increment view count atomically to prevent race conditions
        BlogPost.objects.filter(pk=instance.pk).update(views=F('views') + 1)
        # Refresh instance to get updated view count
        instance.refresh_from_db()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class FeaturedBlogPostsView(generics.ListAPIView):
    """
    API view to list only featured blog posts.
    
    Returns a curated list of blog posts marked as 'featured' by administrators.
    Useful for highlighting important or popular content on the homepage
    or in special sections. Posts are ordered by publication date (newest first).
    """
    queryset = BlogPost.objects.filter(status='published', featured=True)
    serializer_class = BlogPostListSerializer
    ordering = ['-published_at']


class CategoryListView(generics.ListAPIView):
    """
    API view to list all available blog categories.
    
    Provides a complete list of blog categories for navigation menus,
    filtering interfaces, and content organization. Categories help
    users discover related content and improve site navigation.
    """
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class TagListView(generics.ListAPIView):
    """
    API view to list all available blog tags.
    
    Returns all tags used across blog posts, enabling tag-based filtering
    and content discovery. Tags provide more granular content labeling
    compared to categories and support multiple assignments per post.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class CommentCreateView(generics.CreateAPIView):
    """
    API view to create new comments on blog posts.
    
    Handles comment submission with automatic post association and validation.
    Comments are created in an unapproved state by default, requiring
    moderation before public display. This helps maintain content quality
    and prevent spam.
    
    The view automatically associates comments with the correct blog post
    using the post slug from the URL parameters.
    """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def perform_create(self, serializer):
        """
        Override perform_create to associate comment with the correct blog post.
        
        Args:
            serializer: Comment serializer instance with validated data
            
        Raises:
            Http404: If the specified blog post doesn't exist or isn't published
        """
        post_slug = self.kwargs.get('post_slug')
        try:
            post = BlogPost.objects.get(slug=post_slug, status='published')
            serializer.save(post=post)
        except BlogPost.DoesNotExist:
            return Response(
                {'error': 'Blog post not found'}, 
                status=status.HTTP_404_NOT_FOUND
            )


@api_view(['GET'])
def blog_stats(request):
    """
    API endpoint to retrieve comprehensive blog statistics.
    
    Provides key metrics about the blog content including:
    - Total number of published blog posts
    - Total number of categories in use
    - Total number of tags available
    - Total number of approved comments
    
    This endpoint is useful for dashboard displays, analytics widgets,
    and providing overview information to administrators or visitors.
    
    Args:
        request: HTTP GET request object
        
    Returns:
        Response: JSON object containing blog statistics with keys:
            - total_posts: Number of published blog posts
            - total_categories: Number of categories
            - total_tags: Number of tags
            - total_comments: Number of approved comments
    """
    stats = {
        'total_posts': BlogPost.objects.filter(status='published').count(),
        'total_categories': Category.objects.count(),
        'total_tags': Tag.objects.count(),
        'total_comments': Comment.objects.filter(approved=True).count(),
    }
    return Response(stats)


@api_view(['GET'])
def recent_posts(request):
    """
    API endpoint to retrieve the most recently published blog posts.
    
    Returns the 5 most recent published blog posts, ordered by publication date.
    This endpoint is commonly used for "Recent Posts" widgets, sidebar content,
    or homepage highlights to showcase fresh content.
    
    Args:
        request: HTTP GET request object
        
    Returns:
        Response: JSON array of the 5 most recent published blog posts,
                 serialized with BlogPostListSerializer for consistent formatting
    """
    posts = BlogPost.objects.filter(status='published').order_by('-published_at')[:5]
    serializer = BlogPostListSerializer(posts, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def popular_posts(request):
    """
    API endpoint to retrieve the most popular blog posts based on view count.
    
    Returns the top 5 blog posts with the highest view counts, providing
    insights into reader preferences and trending content. This data is
    valuable for content recommendations and understanding audience interests.
    
    Args:
        request: HTTP GET request object
        
    Returns:
        Response: JSON array of the 5 most viewed published blog posts,
                 ordered by view count (highest first), serialized with
                 BlogPostListSerializer for consistent formatting
    """
    posts = BlogPost.objects.filter(status='published').order_by('-views')[:5]
    serializer = BlogPostListSerializer(posts, many=True)
    return Response(serializer.data)
