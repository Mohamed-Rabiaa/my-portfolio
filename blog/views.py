"""
Blog application views for handling blog post, category, tag, and comment operations.

This module provides REST API views for the blog functionality including:
- Blog post listing, detail viewing, and filtering
- Category and tag management
- Comment creation and moderation
- Blog statistics and analytics
- Featured and popular post endpoints
"""

import logging
import time
from rest_framework import generics, filters, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import F
from django.shortcuts import get_object_or_404
from django.views.decorators.cache import cache_page
from django.utils.decorators import method_decorator
from django.http import Http404

from .models import BlogPost, Category, Tag, Comment
from .serializers import (
    BlogPostSerializer, BlogPostListSerializer, CategorySerializer,
    TagSerializer, CommentSerializer
)
from .services import BlogPostService, CategoryService, TagService, CommentService
from common.pagination import BlogPagination, StandardResultsSetPagination, BaseFilteredViewMixin
from common.exceptions import BlogPostNotFound, BlogPostNotPublished, NotFoundError
from common.cache import BlogCache, CacheManager, cache_result
from common.versioning import VersionCompatibilityMixin, deprecated_api
from common.monitoring import monitor_performance, PerformanceMonitor

# Initialize loggers
logger = logging.getLogger('blog')
performance_logger = logging.getLogger('performance')

@method_decorator(cache_page(60 * 30), name='dispatch')  # Cache for 30 minutes
class BlogPostListView(BaseFilteredViewMixin, VersionCompatibilityMixin, generics.ListAPIView):
    """
    API view to list published blog posts with pagination, filtering, and search.
    
    Supports filtering by category, tag, date range filtering, and search functionality.
    Results are cached for 30 minutes to improve performance.
    Performance monitoring tracks query execution times and metrics.
    """
    serializer_class = BlogPostSerializer
    pagination_class = BlogPagination
    search_fields = ['title', 'content', 'excerpt']
    ordering_fields = ['created_at', 'updated_at', 'views']
    ordering = ['-created_at']

    def get_queryset(self):
        """Get published blog posts with performance monitoring."""
        with PerformanceMonitor('blog_posts_query'):
            logger.info("Fetching published blog posts list")
            
            # Get query parameters for logging
            category = self.request.query_params.get('category__slug')
            tags = self.request.query_params.get('tags__slug')
            search = self.request.query_params.get('search')
            
            if category:
                logger.debug(f"Filtering by category: {category}")
            if tags:
                logger.debug(f"Filtering by tags: {tags}")
            if search:
                logger.debug(f"Search query: {search}")
            
            return BlogPostService.get_published_posts()

    def list(self, request, *args, **kwargs):
        """Override list method with performance monitoring."""
        with PerformanceMonitor('blog_list_response'):
            logger.info(f"Blog posts list requested by {request.user}")
            return super().list(request, *args, **kwargs)


class BlogPostDetailView(VersionCompatibilityMixin, generics.RetrieveAPIView):
    """
    API view to retrieve a single blog post by slug.
    
    Increments view count and uses caching for better performance.
    Only returns published posts to public users.
    Performance monitoring tracks retrieval and caching operations.
    """
    serializer_class = BlogPostSerializer
    lookup_field = 'slug'

    def get_object(self):
        with PerformanceMonitor('blog_post_detail_query'):
            slug = self.kwargs.get('slug')
            
            # Try to get from cache first
            cache_key = BlogCache.get_post_key(slug)
            cached_post = CacheManager.get(cache_key)
            
            if cached_post:
                # Still increment view count for cached posts
                BlogPostService.increment_view_count(cached_post)
                return cached_post
            
            try:
                post = BlogPostService.get_post_by_slug(slug)
                BlogPostService.increment_view_count(post)
                
                # Cache the post for future requests
                CacheManager.set(cache_key, post, cache_type='blog_post')
                
                return post
            except BlogPostNotFound:
                raise Http404("Blog post not found")
            except BlogPostNotPublished:
                raise Http404("Blog post not available")


@method_decorator(cache_page(60 * 60), name='dispatch')  # Cache for 1 hour
class FeaturedBlogPostsView(generics.ListAPIView):
    """
    API view to list featured blog posts for homepage or special sections.
    
    Returns only published posts marked as featured, ordered by publication date.
    Results are cached for 1 hour since featured posts change infrequently.
    Performance monitoring tracks featured content queries.
    """
    serializer_class = BlogPostListSerializer
    ordering = ['-published_at']

    def get_queryset(self):
        """Get featured posts using service layer with performance monitoring."""
        with PerformanceMonitor('featured_posts_query'):
            return BlogPostService.get_featured_posts()


@method_decorator(cache_page(60 * 120), name='dispatch')  # Cache for 2 hours
class CategoryListView(generics.ListAPIView):
    """
    API view to list all blog categories with post counts.
    
    Returns categories using the service layer with post counts and metadata.
    Results are cached for 2 hours since categories change infrequently.
    Performance monitoring tracks category retrieval operations.
    """
    serializer_class = CategorySerializer

    def get_queryset(self):
        with PerformanceMonitor('categories_query'):
            return CategoryService.get_all_categories()


@method_decorator(cache_page(60 * 120), name='dispatch')  # Cache for 2 hours
class TagListView(generics.ListAPIView):
    """
    API view to list popular tags with usage counts and popularity metrics.
    
    Returns tags using the service layer, ordered by popularity.
    Results are cached for 2 hours since tag popularity changes slowly.
    Performance monitoring tracks tag retrieval operations.
    """
    serializer_class = TagSerializer

    def get_queryset(self):
        with PerformanceMonitor('tags_query'):
            return TagService.get_popular_tags()


class CommentCreateView(generics.CreateAPIView):
    """
    API view to create new comments on blog posts.
    
    Handles comment submission with automatic post association and validation.
    Comments are created in an unapproved state by default, requiring
    moderation before public display. This helps maintain content quality
    and prevent spam.
    
    The view automatically associates comments with the correct blog post
    using the post slug from the URL parameters.
    Performance monitoring tracks comment creation operations.
    """
    serializer_class = CommentSerializer

    def perform_create(self, serializer):
        """
        Override perform_create to associate comment with the correct blog post.
        
        Args:
            serializer: Comment serializer instance with validated data
            
        Raises:
            Http404: If the specified blog post doesn't exist or isn't published
        """
        with PerformanceMonitor('comment_creation'):
            post_slug = self.kwargs.get('post_slug')
            try:
                post = BlogPostService.get_post_by_slug(post_slug, published_only=True)
                CommentService.create_comment(
                    post=post,
                    name=serializer.validated_data['name'],
                    email=serializer.validated_data['email'],
                    content=serializer.validated_data['content']
                )
            except (BlogPostNotFound, BlogPostNotPublished):
                return Response(
                    {'error': 'Blog post not found'}, 
                    status=status.HTTP_404_NOT_FOUND
                )


@cache_result(timeout=900, cache_type='stats')  # Cache for 15 minutes
@monitor_performance('blog.blog_stats')
@api_view(['GET'])
def blog_stats(request):
    """
    API endpoint to get blog statistics.
    
    Returns comprehensive blog statistics including post counts,
    category distribution, and engagement metrics.
    Results are cached for 15 minutes for better performance.
    Performance monitoring tracks statistics generation.
    """
    with PerformanceMonitor('blog_stats_query'):
        stats = BlogPostService.get_blog_stats()
        return Response(stats)


@cache_result(timeout=600, cache_type='recent')  # Cache for 10 minutes
@monitor_performance('blog.recent_posts')
@api_view(['GET'])
def recent_posts(request):
    """
    API endpoint to get recent blog posts.
    
    Returns the 5 most recently published blog posts.
    Results are cached for 10 minutes for better performance.
    Performance monitoring tracks recent posts retrieval.
    """
    with PerformanceMonitor('recent_posts_query'):
        posts = BlogPostService.get_recent_posts(limit=5)
        serializer = BlogPostSerializer(posts, many=True)
        return Response(serializer.data)


@cache_result(timeout=1800, cache_type='popular')  # Cache for 30 minutes
@monitor_performance('blog.popular_posts')
@api_view(['GET'])
def popular_posts(request):
    """
    API endpoint to get popular blog posts.
    
    Returns the 5 most popular blog posts based on view count.
    Results are cached for 30 minutes since popularity changes slowly.
    Performance monitoring tracks popular posts retrieval.
    """
    with PerformanceMonitor('popular_posts_query'):
        posts = BlogPostService.get_popular_posts(limit=5)
        serializer = BlogPostSerializer(posts, many=True)
        return Response(serializer.data)
