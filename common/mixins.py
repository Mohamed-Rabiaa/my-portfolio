"""
Common model mixins for the portfolio application.

This module provides reusable abstract model classes that can be inherited
by other models to add common functionality like timestamps, slug generation,
and other shared behaviors.
"""

from django.db import models
from django.utils.text import slugify


class TimestampMixin(models.Model):
    """
    Abstract model mixin that provides automatic timestamp fields.
    
    Adds created_at and updated_at fields to any model that inherits from it.
    The created_at field is set once when the object is created, while
    updated_at is updated every time the object is saved.
    
    Usage:
        class MyModel(TimestampMixin):
            name = models.CharField(max_length=100)
            # Automatically gets created_at and updated_at fields
    """
    created_at = models.DateTimeField(
        auto_now_add=True,
        help_text="Timestamp when the object was created"
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        help_text="Timestamp when the object was last updated"
    )

    class Meta:
        abstract = True


class SlugMixin(models.Model):
    """
    Abstract model mixin that provides automatic slug generation.
    
    Adds a slug field and automatically generates it from either a 'title'
    or 'name' field when the object is saved. The slug is only generated
    if it's empty, preserving custom slugs.
    
    Requirements:
        - The model must have either a 'title' or 'name' field
        - The slug field is unique by default
    
    Usage:
        class MyModel(SlugMixin):
            title = models.CharField(max_length=200)
            # Automatically gets slug field and generation logic
    """
    slug = models.SlugField(
        unique=True,
        blank=True,
        help_text="URL-friendly version of the title/name"
    )

    def save(self, *args, **kwargs):
        """
        Override save method to generate slug if not provided.
        
        Generates slug from 'title' field first, then falls back to 'name'.
        Only generates if slug is empty to preserve custom slugs.
        """
        if not self.slug:
            # Try to get slug source from title first, then name
            slug_source = getattr(self, 'title', None) or getattr(self, 'name', None)
            if slug_source:
                self.slug = slugify(slug_source)
        super().save(*args, **kwargs)

    class Meta:
        abstract = True


class BaseModel(TimestampMixin, SlugMixin):
    """
    Base abstract model that combines common mixins.
    
    Provides both timestamp functionality and slug generation.
    Use this as a base for models that need both features.
    
    Usage:
        class MyModel(BaseModel):
            title = models.CharField(max_length=200)
            # Gets created_at, updated_at, and slug fields automatically
    """
    
    class Meta:
        abstract = True


class StatusMixin(models.Model):
    """
    Abstract model mixin for models that need status tracking.
    
    Provides a generic status field with common status choices.
    Can be extended or overridden in specific models.
    """
    STATUS_CHOICES = [
        ('active', 'Active'),
        ('inactive', 'Inactive'),
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    ]
    
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='draft',
        help_text="Current status of the object"
    )

    class Meta:
        abstract = True

    @property
    def is_active(self):
        """Check if the object is in active status."""
        return self.status == 'active'

    @property
    def is_published(self):
        """Check if the object is published."""
        return self.status == 'published'


class OrderingMixin(models.Model):
    """
    Abstract model mixin for models that need manual ordering.
    
    Provides an order field for custom sorting of objects.
    Lower numbers appear first in ordering.
    """
    order = models.PositiveIntegerField(
        default=0,
        help_text="Order for sorting (lower numbers appear first)"
    )

    class Meta:
        abstract = True
        ordering = ['order']