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
    """List published blog posts with filtering and search"""
    queryset = BlogPost.objects.filter(status='published')
    serializer_class = BlogPostListSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'tags', 'featured', 'author']
    search_fields = ['title', 'excerpt', 'content', 'tags__name']
    ordering_fields = ['published_at', 'views', 'title']
    ordering = ['-published_at']


class BlogPostDetailView(generics.RetrieveAPIView):
    """Retrieve a single blog post by slug and increment views"""
    queryset = BlogPost.objects.filter(status='published')
    serializer_class = BlogPostSerializer
    lookup_field = 'slug'

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        # Increment view count
        BlogPost.objects.filter(pk=instance.pk).update(views=F('views') + 1)
        # Refresh instance to get updated view count
        instance.refresh_from_db()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


class FeaturedBlogPostsView(generics.ListAPIView):
    """List featured blog posts only"""
    queryset = BlogPost.objects.filter(status='published', featured=True)
    serializer_class = BlogPostListSerializer
    ordering = ['-published_at']


class CategoryListView(generics.ListAPIView):
    """List all blog categories"""
    queryset = Category.objects.all()
    serializer_class = CategorySerializer


class TagListView(generics.ListAPIView):
    """List all blog tags"""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class CommentCreateView(generics.CreateAPIView):
    """Create a new comment for a blog post"""
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer

    def perform_create(self, serializer):
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
    """Get blog statistics"""
    stats = {
        'total_posts': BlogPost.objects.filter(status='published').count(),
        'featured_posts': BlogPost.objects.filter(status='published', featured=True).count(),
        'total_categories': Category.objects.count(),
        'total_tags': Tag.objects.count(),
        'total_comments': Comment.objects.filter(approved=True).count(),
        'posts_by_category': {}
    }
    
    # Get posts count by category
    for category in Category.objects.all():
        stats['posts_by_category'][category.name] = category.posts.filter(status='published').count()
    
    return Response(stats)


@api_view(['GET'])
def recent_posts(request):
    """Get recent blog posts"""
    limit = int(request.GET.get('limit', 5))
    posts = BlogPost.objects.filter(status='published')[:limit]
    serializer = BlogPostListSerializer(posts, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def popular_posts(request):
    """Get popular blog posts by views"""
    limit = int(request.GET.get('limit', 5))
    posts = BlogPost.objects.filter(status='published').order_by('-views')[:limit]
    serializer = BlogPostListSerializer(posts, many=True)
    return Response(serializer.data)
