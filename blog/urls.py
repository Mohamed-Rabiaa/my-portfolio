from django.urls import path
from . import views

app_name = 'blog'

urlpatterns = [
    # Blog post endpoints
    path('posts/', views.BlogPostListView.as_view(), name='post-list'),
    path('posts/<slug:slug>/', views.BlogPostDetailView.as_view(), name='post-detail'),
    path('posts/featured/', views.FeaturedBlogPostsView.as_view(), name='featured-posts'),
    path('posts/recent/', views.recent_posts, name='recent-posts'),
    path('posts/popular/', views.popular_posts, name='popular-posts'),
    
    # Category and tag endpoints
    path('categories/', views.CategoryListView.as_view(), name='category-list'),
    path('tags/', views.TagListView.as_view(), name='tag-list'),
    
    # Comment endpoints
    path('posts/<slug:post_slug>/comments/', views.CommentCreateView.as_view(), name='comment-create'),
    
    # Statistics
    path('stats/', views.blog_stats, name='blog-stats'),
]