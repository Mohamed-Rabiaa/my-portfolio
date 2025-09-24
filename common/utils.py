"""
Utility functions and constants for the portfolio application.

This module contains reusable utility functions, constants, and helper
methods that are used across multiple apps in the portfolio project.
"""

import re
import hashlib
import secrets
from typing import Optional, Dict, Any, List
from django.utils.text import slugify
from django.core.exceptions import ValidationError
from django.core.validators import validate_email
from django.utils import timezone
from datetime import datetime, timedelta


# Constants
class StatusChoices:
    """Standard status choices used across models."""
    DRAFT = 'draft'
    PUBLISHED = 'published'
    ARCHIVED = 'archived'
    
    CHOICES = [
        (DRAFT, 'Draft'),
        (PUBLISHED, 'Published'),
        (ARCHIVED, 'Archived'),
    ]


class PriorityChoices:
    """Priority levels for various content."""
    LOW = 'low'
    MEDIUM = 'medium'
    HIGH = 'high'
    URGENT = 'urgent'
    
    CHOICES = [
        (LOW, 'Low'),
        (MEDIUM, 'Medium'),
        (HIGH, 'High'),
        (URGENT, 'Urgent'),
    ]


# Utility Functions
def generate_unique_slug(title: str, model_class, max_length: int = 50) -> str:
    """
    Generate a unique slug for a given title and model class.
    
    Args:
        title: The title to create a slug from
        model_class: The Django model class to check for uniqueness
        max_length: Maximum length of the slug
        
    Returns:
        A unique slug string
    """
    base_slug = slugify(title)[:max_length]
    slug = base_slug
    counter = 1
    
    while model_class.objects.filter(slug=slug).exists():
        suffix = f"-{counter}"
        max_base_length = max_length - len(suffix)
        slug = f"{base_slug[:max_base_length]}{suffix}"
        counter += 1
    
    return slug


def sanitize_html_input(text: str) -> str:
    """
    Basic HTML sanitization for user input.
    
    Removes potentially dangerous HTML tags while preserving safe formatting.
    
    Args:
        text: The input text to sanitize
        
    Returns:
        Sanitized text string
    """
    if not text:
        return ""
    
    # Remove script tags and their content
    text = re.sub(r'<script[^>]*>.*?</script>', '', text, flags=re.DOTALL | re.IGNORECASE)
    
    # Remove dangerous attributes
    dangerous_attrs = ['onclick', 'onload', 'onerror', 'onmouseover', 'onfocus', 'onblur']
    for attr in dangerous_attrs:
        text = re.sub(rf'{attr}=["\'][^"\']*["\']', '', text, flags=re.IGNORECASE)
    
    # Remove javascript: links
    text = re.sub(r'javascript:', '', text, flags=re.IGNORECASE)
    
    return text.strip()


def validate_email_address(email: str) -> bool:
    """
    Validate email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if email is valid, False otherwise
    """
    try:
        validate_email(email)
        return True
    except ValidationError:
        return False


def generate_cache_key(*args, **kwargs) -> str:
    """
    Generate a consistent cache key from arguments.
    
    Args:
        *args: Positional arguments to include in key
        **kwargs: Keyword arguments to include in key
        
    Returns:
        A hash-based cache key string
    """
    key_parts = []
    
    # Add positional arguments
    for arg in args:
        key_parts.append(str(arg))
    
    # Add keyword arguments (sorted for consistency)
    for key, value in sorted(kwargs.items()):
        key_parts.append(f"{key}:{value}")
    
    # Create hash of combined parts
    key_string = "|".join(key_parts)
    return hashlib.md5(key_string.encode()).hexdigest()


def truncate_text(text: str, max_length: int = 150, suffix: str = "...") -> str:
    """
    Truncate text to a maximum length with a suffix.
    
    Args:
        text: Text to truncate
        max_length: Maximum length including suffix
        suffix: Suffix to add when truncating
        
    Returns:
        Truncated text string
    """
    if not text or len(text) <= max_length:
        return text
    
    truncated_length = max_length - len(suffix)
    return text[:truncated_length].rstrip() + suffix


def get_client_ip(request) -> str:
    """
    Get the client IP address from a Django request.
    
    Handles various proxy headers to get the real client IP.
    
    Args:
        request: Django HttpRequest object
        
    Returns:
        Client IP address as string
    """
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0].strip()
    else:
        ip = request.META.get('REMOTE_ADDR', '')
    
    return ip


def format_reading_time(word_count: int, words_per_minute: int = 200) -> str:
    """
    Calculate and format reading time for content.
    
    Args:
        word_count: Number of words in the content
        words_per_minute: Average reading speed
        
    Returns:
        Formatted reading time string (e.g., "5 min read")
    """
    if word_count <= 0:
        return "< 1 min read"
    
    minutes = max(1, round(word_count / words_per_minute))
    
    if minutes == 1:
        return "1 min read"
    else:
        return f"{minutes} min read"


def get_word_count(text: str) -> int:
    """
    Count words in a text string.
    
    Args:
        text: Text to count words in
        
    Returns:
        Number of words
    """
    if not text:
        return 0
    
    # Remove HTML tags for accurate word count
    clean_text = re.sub(r'<[^>]+>', ' ', text)
    words = clean_text.split()
    return len(words)


def generate_api_key(length: int = 32) -> str:
    """
    Generate a secure API key.
    
    Args:
        length: Length of the API key
        
    Returns:
        Secure random API key string
    """
    return secrets.token_urlsafe(length)


def is_recent(timestamp: datetime, hours: int = 24) -> bool:
    """
    Check if a timestamp is within the specified number of hours.
    
    Args:
        timestamp: Datetime to check
        hours: Number of hours to consider as "recent"
        
    Returns:
        True if timestamp is recent, False otherwise
    """
    if not timestamp:
        return False
    
    cutoff = timezone.now() - timedelta(hours=hours)
    return timestamp >= cutoff


def parse_tags(tag_string: str) -> List[str]:
    """
    Parse a comma-separated string of tags into a list.
    
    Args:
        tag_string: Comma-separated tags string
        
    Returns:
        List of cleaned tag strings
    """
    if not tag_string:
        return []
    
    tags = [tag.strip().lower() for tag in tag_string.split(',')]
    return [tag for tag in tags if tag]  # Remove empty tags


def build_absolute_url(request, path: str) -> str:
    """
    Build an absolute URL from a request and path.
    
    Args:
        request: Django HttpRequest object
        path: URL path to make absolute
        
    Returns:
        Absolute URL string
    """
    return request.build_absolute_uri(path)


# Decorators and Context Managers
class timer:
    """
    Context manager for timing code execution.
    
    Usage:
        with timer() as t:
            # some code
        print(f"Execution took {t.elapsed} seconds")
    """
    
    def __enter__(self):
        self.start = timezone.now()
        return self
    
    def __exit__(self, *args):
        self.end = timezone.now()
        self.elapsed = (self.end - self.start).total_seconds()


# Data validation helpers
def validate_required_fields(data: Dict[str, Any], required_fields: List[str]) -> List[str]:
    """
    Validate that required fields are present in data.
    
    Args:
        data: Dictionary of data to validate
        required_fields: List of required field names
        
    Returns:
        List of missing field names
    """
    missing_fields = []
    
    for field in required_fields:
        if field not in data or data[field] is None or data[field] == '':
            missing_fields.append(field)
    
    return missing_fields