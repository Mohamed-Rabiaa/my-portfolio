"""
Service layer for blog functionality.

This module contains business logic for blog operations, separating concerns
from views and providing reusable methods for blog-related operations.
"""

import logging
import time
from typing import List, Optional, Dict, Any
from django.db.models import QuerySet, F, Q, Prefetch, Count
from django.utils import timezone
from django.core.exceptions import ValidationError
from django.contrib.auth.models import User

from .models import BlogPost, Category, Tag, Comment
from common.exceptions import (
    BlogPostNotFound, 
    BlogPostNotPublished, 
    ValidationError as CustomValidationError,
    NotFoundError
)
from common.utils import StatusChoices, generate_unique_slug, get_word_count, format_reading_time

# Initialize loggers
logger = logging.getLogger('blog')
performance_logger = logging.getLogger('performance')


class BlogPostService:
    """
    Service class for blog post operations.
    
    Handles all business logic related to blog posts including creation,
    retrieval, updates, and publishing workflows.
    """
    
    @staticmethod
    def get_published_posts(category_slug=None, tag_slug=None, featured_only=False):
        """
        Get published blog posts with optional filtering and optimized queries.
        
        Args:
            category_slug: Filter by category slug
            tag_slug: Filter by tag slug
            featured_only: Only return featured posts
            
        Returns:
            QuerySet of published blog posts
        """
        start_time = time.time()
        logger.info(f"Fetching published posts - category: {category_slug}, tag: {tag_slug}, featured_only: {featured_only}")
        
        try:
            queryset = BlogPost.objects.select_related(
                'category', 'author'
            ).prefetch_related(
                'tags', 'comments'
            ).filter(status='published').order_by('-created_at')
            
            if category_slug:
                queryset = queryset.filter(category__slug=category_slug)
                logger.debug(f"Applied category filter: {category_slug}")
            
            if tag_slug:
                queryset = queryset.filter(tags__slug=tag_slug)
                logger.debug(f"Applied tag filter: {tag_slug}")
            
            if featured_only:
                queryset = queryset.filter(featured=True)
                logger.debug("Applied featured filter")
            
            result_count = queryset.count()
            execution_time = time.time() - start_time
            
            logger.info(f"Successfully fetched {result_count} published posts")
            performance_logger.info(f"get_published_posts executed in {execution_time:.3f}s, returned {result_count} posts")
            
            return queryset
            
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Error fetching published posts: {str(e)}", exc_info=True)
            performance_logger.info(f"get_published_posts failed in {execution_time:.3f}s")
            raise
    
    @staticmethod
    def get_post_by_slug(slug, published_only=True):
        """
        Get a blog post by its slug with optimized queries.
        
        Args:
            slug: The post slug
            published_only: Only return published posts
            
        Returns:
            BlogPost instance
            
        Raises:
            BlogPostNotFound: If post doesn't exist
            BlogPostNotPublished: If post exists but isn't published
        """
        start_time = time.time()
        logger.info(f"Fetching post by slug: {slug}, published_only: {published_only}")
        
        try:
            queryset = BlogPost.objects.select_related(
                'category'
            ).prefetch_related(
                'tags', 
                Prefetch('comments', queryset=Comment.objects.filter(approved=True))
            )
            
            try:
                post = queryset.get(slug=slug)
                logger.debug(f"Found post: {post.title} (status: {post.status})")
                
                if published_only and post.status != 'published':
                    logger.warning(f"Post {slug} exists but is not published (status: {post.status})")
                    raise BlogPostNotPublished(f"Post '{slug}' is not published")
                
                execution_time = time.time() - start_time
                logger.info(f"Successfully retrieved post: {post.title}")
                performance_logger.info(f"get_post_by_slug executed in {execution_time:.3f}s for slug: {slug}")
                
                return post
                
            except BlogPost.DoesNotExist:
                logger.warning(f"Post with slug '{slug}' not found")
                raise BlogPostNotFound(f"Post with slug '{slug}' not found")
                
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Error fetching post by slug {slug}: {str(e)}", exc_info=True)
            performance_logger.info(f"get_post_by_slug failed in {execution_time:.3f}s for slug: {slug}")
            raise
    
    @staticmethod
    def increment_view_count(post: BlogPost) -> BlogPost:
        """
        Increment the view count for a blog post.
        
        Args:
            post: BlogPost instance
            
        Returns:
            Updated BlogPost instance
        """
        BlogPost.objects.filter(pk=post.pk).update(views=F('views') + 1)
        post.refresh_from_db(fields=['views'])
        return post
    
    @staticmethod
    def create_post(
        title: str,
        content: str,
        excerpt: str,
        author: User,
        category: Optional[Category] = None,
        tags: Optional[List[Tag]] = None,
        featured_image=None,
        status: str = StatusChoices.DRAFT,
        featured: bool = False
    ) -> BlogPost:
        """
        Create a new blog post.
        
        Args:
            title: Post title
            content: Post content
            excerpt: Post excerpt
            author: Post author
            category: Optional category
            tags: Optional list of tags
            featured_image: Optional featured image
            status: Post status (default: draft)
            featured: Whether post is featured
            
        Returns:
            Created BlogPost instance
            
        Raises:
            CustomValidationError: If validation fails
        """
        # Validate required fields
        if not title or not content or not excerpt:
            raise CustomValidationError("Title, content, and excerpt are required")
        
        # Calculate reading time
        word_count = get_word_count(content)
        read_time = max(1, round(word_count / 200))  # 200 words per minute
        
        # Generate unique slug
        slug = generate_unique_slug(title, BlogPost)
        
        # Create the post
        post = BlogPost.objects.create(
            title=title,
            slug=slug,
            content=content,
            excerpt=excerpt,
            author=author,
            category=category,
            featured_image=featured_image,
            status=status,
            featured=featured,
            read_time=read_time
        )
        
        # Add tags if provided
        if tags:
            post.tags.set(tags)
        
        return post
    
    @staticmethod
    def update_post(
        post: BlogPost,
        **kwargs
    ) -> BlogPost:
        """
        Update an existing blog post.
        
        Args:
            post: BlogPost instance to update
            **kwargs: Fields to update
            
        Returns:
            Updated BlogPost instance
        """
        # Update reading time if content changed
        if 'content' in kwargs:
            word_count = get_word_count(kwargs['content'])
            kwargs['read_time'] = max(1, round(word_count / 200))
        
        # Update fields
        for field, value in kwargs.items():
            if hasattr(post, field):
                setattr(post, field, value)
        
        post.save()
        return post
    
    @staticmethod
    def publish_post(post: BlogPost) -> BlogPost:
        """
        Publish a blog post.
        
        Args:
            post: BlogPost instance to publish
            
        Returns:
            Published BlogPost instance
        """
        post.status = StatusChoices.PUBLISHED
        if not post.published_at:
            post.published_at = timezone.now()
        post.save()
        return post
    
    @staticmethod
    def get_featured_posts(limit=5):
        """
        Get featured blog posts with optimized queries.
        
        Args:
            limit: Maximum number of posts to return
            
        Returns:
            QuerySet of featured blog posts
        """
        return BlogPost.objects.select_related(
            'category', 'author'
        ).prefetch_related(
            'tags'
        ).filter(
            status='published', 
            featured=True
        ).order_by('-created_at')[:limit]

    @staticmethod
    def get_recent_posts(limit=5):
        """
        Get recent blog posts with optimized queries.
        
        Args:
            limit: Maximum number of posts to return
            
        Returns:
            QuerySet of recent blog posts
        """
        return BlogPost.objects.select_related(
            'category', 'author'
        ).prefetch_related(
            'tags'
        ).filter(
            status='published'
        ).order_by('-created_at')[:limit]

    @staticmethod
    def get_popular_posts(limit=5):
        """
        Get popular blog posts based on view count with optimized queries.
        
        Args:
            limit: Maximum number of posts to return
            
        Returns:
            QuerySet of popular blog posts
        """
        return BlogPost.objects.select_related(
            'category', 'author'
        ).prefetch_related(
            'tags'
        ).filter(
            status='published'
        ).order_by('-view_count', '-created_at')[:limit]

    @staticmethod
    def get_blog_stats() -> Dict[str, int]:
        """
        Get comprehensive blog statistics.
        
        Returns:
            Dictionary containing blog statistics
        """
        from .models import Category, Tag, Comment
        
        return {
            'total_posts': BlogPost.objects.count(),
            'published_posts': BlogPost.objects.filter(status=StatusChoices.PUBLISHED).count(),
            'total_categories': Category.objects.count(),
            'total_tags': Tag.objects.count(),
            'total_comments': Comment.objects.filter(approved=True).count(),
        }

    @staticmethod
    def get_related_posts(post: BlogPost, limit: int = 3) -> QuerySet[BlogPost]:
        """
        Get related posts based on category and tags.
        
        Args:
            post: BlogPost to find related posts for
            limit: Maximum number of related posts
            
        Returns:
            QuerySet of related posts
        """
        related_posts = BlogPost.objects.filter(
            status=StatusChoices.PUBLISHED
        ).exclude(
            pk=post.pk
        ).select_related('author', 'category')
        
        # Prioritize posts from same category
        if post.category:
            related_posts = related_posts.filter(
                Q(category=post.category) | Q(tags__in=post.tags.all())
            ).distinct()
        else:
            related_posts = related_posts.filter(
                tags__in=post.tags.all()
            ).distinct()
        
        return related_posts[:limit]


class CategoryService:
    """Service class for category operations."""
    
    @staticmethod
    def get_categories_with_counts():
        """
        Get all categories with post counts using optimized queries.
        
        Returns:
            QuerySet of categories with post counts
        """
        from django.db.models import Count
        
        return Category.objects.annotate(
            post_count=Count('blogpost', filter=Q(blogpost__status='published'))
        ).filter(post_count__gt=0).order_by('name')
    
    @staticmethod
    def get_category_by_slug(slug: str) -> Category:
        """
        Get category by slug.
        
        Args:
            slug: Category slug
            
        Returns:
            Category instance
            
        Raises:
            NotFoundError: If category doesn't exist
        """
        try:
            return Category.objects.get(slug=slug)
        except Category.DoesNotExist:
            raise NotFoundError("Category", slug)


class TagService:
    """Service class for tag operations."""
    
    @staticmethod
    def get_popular_tags(limit: int = 10) -> QuerySet[Tag]:
        """
        Get popular tags based on usage count.
        
        Args:
            limit: Maximum number of tags to return
            
        Returns:
            QuerySet of popular tags
        """
        return Tag.objects.annotate(
            post_count=Count('posts', filter=Q(posts__status=StatusChoices.PUBLISHED))
        ).filter(post_count__gt=0).order_by('-post_count')[:limit]
    
    @staticmethod
    def get_tags_with_counts():
        """
        Get all tags with post counts using optimized queries.
        
        Returns:
            QuerySet of tags with post counts
        """
        from django.db.models import Count
        
        return Tag.objects.annotate(
            post_count=Count('blogpost', filter=Q(blogpost__status='published'))
        ).filter(post_count__gt=0).order_by('-post_count', 'name')
    
    @staticmethod
    def get_tag_by_slug(slug: str) -> Tag:
        """
        Get tag by slug.
        
        Args:
            slug: Tag slug
            
        Returns:
            Tag instance
            
        Raises:
            NotFoundError: If tag doesn't exist
        """
        try:
            return Tag.objects.get(slug=slug)
        except Tag.DoesNotExist:
            raise NotFoundError("Tag", slug)


class CommentService:
    """Service class for comment operations."""
    
    @staticmethod
    def get_approved_comments(post: BlogPost) -> QuerySet[Comment]:
        """
        Get approved comments for a post.
        
        Args:
            post: BlogPost instance
            
        Returns:
            QuerySet of approved comments
        """
        return Comment.objects.filter(
            post=post,
            approved=True
        ).order_by('created_at')
    
    @staticmethod
    def create_comment(
        post: BlogPost,
        name: str,
        email: str,
        content: str
    ) -> Comment:
        """
        Create a new comment.
        
        Args:
            post: BlogPost to comment on
            name: Commenter name
            email: Commenter email
            content: Comment content
            
        Returns:
            Created Comment instance
            
        Raises:
            CustomValidationError: If validation fails
        """
        # Validate required fields
        if not all([name, email, content]):
            raise CustomValidationError("Name, email, and content are required")
        
        return Comment.objects.create(
            post=post,
            name=name,
            email=email,
            content=content,
            approved=False  # Require moderation
        )
    
    @staticmethod
    def approve_comment(comment: Comment) -> Comment:
        """
        Approve a comment.
        
        Args:
            comment: Comment instance to approve
            
        Returns:
            Approved Comment instance
        """
        comment.approved = True
        comment.save()
        return comment