"""
Caching utilities for the portfolio application.

This module provides caching functionality for frequently accessed data
to improve application performance and reduce database queries.
"""

from typing import Any, Optional, List, Dict, Callable
from functools import wraps
from django.core.cache import cache
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
import hashlib
import json

from .utils import generate_cache_key
from .exceptions import PortfolioException


class CacheManager:
    """
    Centralized cache management for the portfolio application.
    
    Provides methods for caching common data patterns and managing
    cache invalidation across related models.
    """
    
    # Cache timeout constants (in seconds)
    CACHE_TIMEOUTS = {
        'blog_post': 3600,  # 1 hour
        'blog_list': 1800,  # 30 minutes
        'project': 3600,    # 1 hour
        'project_list': 1800,  # 30 minutes
        'category': 7200,   # 2 hours
        'tag': 7200,        # 2 hours
        'stats': 900,       # 15 minutes
        'featured': 1800,   # 30 minutes
        'popular': 1800,    # 30 minutes
        'recent': 600,      # 10 minutes
    }
    
    @classmethod
    def get_timeout(cls, cache_type: str) -> int:
        """Get cache timeout for a specific cache type."""
        return cls.CACHE_TIMEOUTS.get(cache_type, 3600)  # Default 1 hour
    
    @classmethod
    def set(cls, key: str, value: Any, timeout: Optional[int] = None, cache_type: str = None) -> bool:
        """
        Set a cache value with optional timeout and type.
        
        Args:
            key: Cache key
            value: Value to cache
            timeout: Cache timeout in seconds
            cache_type: Type of cache for default timeout
            
        Returns:
            True if cached successfully, False otherwise
        """
        try:
            if timeout is None and cache_type:
                timeout = cls.get_timeout(cache_type)
            
            cache.set(key, value, timeout)
            return True
        except Exception as e:
            # Log error in production
            print(f"Cache set error: {e}")
            raise PortfolioException(f"Cache operation failed: {e}")
    
    @classmethod
    def get(cls, key: str, default: Any = None) -> Any:
        """
        Get a cache value.
        
        Args:
            key: Cache key
            default: Default value if key not found
            
        Returns:
            Cached value or default
        """
        try:
            return cache.get(key, default)
        except Exception as e:
            # Log error in production
            print(f"Cache get error: {e}")
            return default
    
    @classmethod
    def delete(cls, key: str) -> bool:
        """
        Delete a cache key.
        
        Args:
            key: Cache key to delete
            
        Returns:
            True if deleted successfully
        """
        try:
            cache.delete(key)
            return True
        except Exception as e:
            # Log error in production
            print(f"Cache delete error: {e}")
            return False
    
    @classmethod
    def delete_pattern(cls, pattern: str) -> int:
        """
        Delete cache keys matching a pattern.
        
        Args:
            pattern: Pattern to match (supports wildcards)
            
        Returns:
            Number of keys deleted
        """
        try:
            if hasattr(cache, 'delete_pattern'):
                return cache.delete_pattern(pattern)
            else:
                # Fallback for cache backends that don't support pattern deletion
                # This is a simplified implementation
                keys_to_delete = []
                if hasattr(cache, '_cache'):
                    for key in cache._cache.keys():
                        if pattern.replace('*', '') in key:
                            keys_to_delete.append(key)
                
                for key in keys_to_delete:
                    cache.delete(key)
                
                return len(keys_to_delete)
        except Exception as e:
            # Log error in production
            print(f"Cache delete pattern error: {e}")
            return 0
    
    @classmethod
    def clear_all(cls) -> bool:
        """
        Clear all cache entries.
        
        Returns:
            True if cleared successfully
        """
        try:
            cache.clear()
            return True
        except Exception as e:
            # Log error in production
            print(f"Cache clear error: {e}")
            return False


class BlogCache:
    """Cache management for blog-related data."""
    
    @staticmethod
    def get_post_key(slug: str) -> str:
        """Generate cache key for a blog post."""
        return generate_cache_key('blog', 'post', slug)
    
    @staticmethod
    def get_posts_list_key(status: str = 'published', page: int = 1, per_page: int = 10) -> str:
        """Generate cache key for blog posts list."""
        return generate_cache_key('blog', 'posts', status, page, per_page)
    
    @staticmethod
    def get_featured_posts_key(limit: int = 5) -> str:
        """Generate cache key for featured posts."""
        return generate_cache_key('blog', 'featured', limit)
    
    @staticmethod
    def get_popular_posts_key(limit: int = 5) -> str:
        """Generate cache key for popular posts."""
        return generate_cache_key('blog', 'popular', limit)
    
    @staticmethod
    def get_recent_posts_key(limit: int = 5) -> str:
        """Generate cache key for recent posts."""
        return generate_cache_key('blog', 'recent', limit)
    
    @staticmethod
    def get_category_posts_key(category_slug: str, page: int = 1) -> str:
        """Generate cache key for category posts."""
        return generate_cache_key('blog', 'category', category_slug, page)
    
    @staticmethod
    def get_tag_posts_key(tag_slug: str, page: int = 1) -> str:
        """Generate cache key for tag posts."""
        return generate_cache_key('blog', 'tag', tag_slug, page)
    
    @staticmethod
    def get_stats_key() -> str:
        """Generate cache key for blog stats."""
        return generate_cache_key('blog', 'stats')
    
    @staticmethod
    def invalidate_post(slug: str) -> None:
        """Invalidate cache for a specific post and related data."""
        # Delete specific post cache
        CacheManager.delete(BlogCache.get_post_key(slug))
        
        # Delete related list caches
        CacheManager.delete_pattern('portfolio:blog:posts:*')
        CacheManager.delete_pattern('portfolio:blog:featured:*')
        CacheManager.delete_pattern('portfolio:blog:popular:*')
        CacheManager.delete_pattern('portfolio:blog:recent:*')
        CacheManager.delete_pattern('portfolio:blog:stats*')
    
    @staticmethod
    def invalidate_all() -> None:
        """Invalidate all blog-related cache."""
        CacheManager.delete_pattern('portfolio:blog:*')


class ProjectCache:
    """Cache management for project-related data."""
    
    @staticmethod
    def get_project_key(slug: str) -> str:
        """Generate cache key for a project."""
        return generate_cache_key('project', slug)
    
    @staticmethod
    def get_projects_list_key(featured: bool = False, page: int = 1) -> str:
        """Generate cache key for projects list."""
        return generate_cache_key('projects', 'featured' if featured else 'all', page)
    
    @staticmethod
    def get_featured_projects_key(limit: int = 6) -> str:
        """Generate cache key for featured projects."""
        return generate_cache_key('projects', 'featured', limit)
    
    @staticmethod
    def get_skills_key() -> str:
        """Generate cache key for skills."""
        return generate_cache_key('skills', 'all')
    
    @staticmethod
    def invalidate_project(slug: str) -> None:
        """Invalidate cache for a specific project and related data."""
        # Delete specific project cache
        CacheManager.delete(ProjectCache.get_project_key(slug))
        
        # Delete related list caches
        CacheManager.delete_pattern('portfolio:projects:*')
    
    @staticmethod
    def invalidate_all() -> None:
        """Invalidate all project-related cache."""
        CacheManager.delete_pattern('portfolio:project*')


def cache_result(timeout: int = 3600, key_func: Optional[Callable] = None, cache_type: str = None):
    """
    Decorator to cache function results.
    
    Args:
        timeout: Cache timeout in seconds
        key_func: Function to generate cache key from arguments
        cache_type: Type of cache for default timeout
        
    Returns:
        Decorated function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            if key_func:
                cache_key = key_func(*args, **kwargs)
            else:
                # Default key generation
                key_parts = [func.__name__]
                key_parts.extend(str(arg) for arg in args)
                key_parts.extend(f"{k}:{v}" for k, v in sorted(kwargs.items()))
                cache_key = generate_cache_key(*key_parts)
            
            # Try to get from cache
            result = CacheManager.get(cache_key)
            if result is not None:
                return result
            
            # Execute function and cache result
            result = func(*args, **kwargs)
            
            # Determine timeout
            actual_timeout = timeout
            if cache_type:
                actual_timeout = CacheManager.get_timeout(cache_type)
            
            CacheManager.set(cache_key, result, actual_timeout)
            return result
        
        return wrapper
    return decorator


def invalidate_cache_on_save(cache_patterns: List[str]):
    """
    Decorator to invalidate cache patterns when a model is saved.
    
    Args:
        cache_patterns: List of cache patterns to invalidate
        
    Returns:
        Decorated function
    """
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            
            # Invalidate cache patterns
            for pattern in cache_patterns:
                CacheManager.delete_pattern(pattern)
            
            return result
        
        return wrapper
    return decorator


class CacheStats:
    """Utility class for cache statistics and monitoring."""
    
    @staticmethod
    def get_cache_info() -> Dict[str, Any]:
        """
        Get cache information and statistics.
        
        Returns:
            Dictionary with cache information
        """
        try:
            if hasattr(cache, 'get_stats'):
                stats = cache.get_stats()
            else:
                stats = {'backend': str(cache.__class__.__name__)}
            
            return {
                'backend': stats.get('backend', 'Unknown'),
                'hits': stats.get('hits', 0),
                'misses': stats.get('misses', 0),
                'keys': stats.get('keys', 0),
                'memory_usage': stats.get('memory_usage', 0),
            }
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def warm_cache() -> Dict[str, int]:
        """
        Warm up cache with frequently accessed data.
        
        Returns:
            Dictionary with warming statistics
        """
        warmed = {'blog_posts': 0, 'projects': 0, 'categories': 0, 'tags': 0}
        
        try:
            # Import here to avoid circular imports
            from blog.services import BlogPostService, CategoryService, TagService
            from portfolio.services import ProjectService
            
            # Warm blog data
            BlogPostService.get_featured_posts()
            BlogPostService.get_popular_posts()
            BlogPostService.get_recent_posts()
            warmed['blog_posts'] = 3
            
            # Warm project data
            ProjectService.get_featured_projects()
            warmed['projects'] = 1
            
            # Warm category and tag data
            CategoryService.get_all_categories()
            TagService.get_popular_tags()
            warmed['categories'] = 1
            warmed['tags'] = 1
            
        except Exception as e:
            # Log error in production
            print(f"Cache warming error: {e}")
        
        return warmed