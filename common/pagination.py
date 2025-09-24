"""
Custom pagination classes and filtering mixins for the portfolio application.

This module provides standardized pagination classes and filtering utilities
that ensure consistent pagination behavior and filtering capabilities across
all API endpoints.
"""

import logging
from django.core.paginator import Paginator
from django.db.models import Q
from django.utils.dateparse import parse_date
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework import filters
from django_filters.rest_framework import DjangoFilterBackend
from collections import OrderedDict

logger = logging.getLogger('api.pagination')


class StandardResultsSetPagination(PageNumberPagination):
    """
    Standard pagination class for most API endpoints.
    
    Provides consistent pagination with reasonable defaults:
    - 20 items per page by default
    - Configurable page size up to 100 items
    - Standard pagination response format
    """
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100
    page_query_param = 'page'

    def get_paginated_response(self, data):
        """
        Return a paginated response with additional metadata.
        
        Includes total count, page information, and navigation links
        for better client-side pagination handling.
        """
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('total_pages', self.page.paginator.num_pages),
            ('current_page', self.page.number),
            ('page_size', self.get_page_size(self.request)),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))


class LargeResultsSetPagination(PageNumberPagination):
    """
    Pagination class for endpoints that may return large datasets.
    
    Uses larger page sizes for better performance when dealing
    with large amounts of data.
    """
    page_size = 50
    page_size_query_param = 'page_size'
    max_page_size = 200
    page_query_param = 'page'

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('total_pages', self.page.paginator.num_pages),
            ('current_page', self.page.number),
            ('page_size', self.get_page_size(self.request)),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))


class SmallResultsSetPagination(PageNumberPagination):
    """
    Pagination class for endpoints with smaller datasets.
    
    Uses smaller page sizes for better user experience when
    browsing through smaller collections.
    """
    page_size = 10
    page_size_query_param = 'page_size'
    max_page_size = 50
    page_query_param = 'page'

    def get_paginated_response(self, data):
        return Response(OrderedDict([
            ('count', self.page.paginator.count),
            ('total_pages', self.page.paginator.num_pages),
            ('current_page', self.page.number),
            ('page_size', self.get_page_size(self.request)),
            ('next', self.get_next_link()),
            ('previous', self.get_previous_link()),
            ('results', data)
        ]))


class BlogPagination(StandardResultsSetPagination):
    """
    Specialized pagination for blog posts.
    
    Optimized for blog reading experience with appropriate page sizes.
    """
    page_size = 12  # Good for grid layouts
    max_page_size = 50


class ProjectPagination(StandardResultsSetPagination):
    """
    Specialized pagination for portfolio projects.
    
    Optimized for project showcase with visual layouts.
    """
    page_size = 9  # Good for 3x3 grid layouts
    max_page_size = 36


class CommentPagination(SmallResultsSetPagination):
    """
    Specialized pagination for comments.
    
    Uses smaller page sizes for better comment thread readability.
    """
    page_size = 15
    max_page_size = 30


class FilterMixin:
    """
    Base mixin providing common filtering functionality.
    
    Provides reusable filtering methods that can be used across
    different viewsets to ensure consistent filtering behavior.
    """
    
    def apply_search_filter(self, queryset, search_term, search_fields):
        """
        Apply search filtering across multiple fields.
        
        Args:
            queryset: The base queryset to filter
            search_term: The search term to look for
            search_fields: List of fields to search in
            
        Returns:
            QuerySet: Filtered queryset
        """
        if not search_term or not search_fields:
            return queryset
        
        search_query = Q()
        for field in search_fields:
            search_query |= Q(**{f"{field}__icontains": search_term})
        
        logger.info(f"Applied search filter: '{search_term}' across fields: {search_fields}")
        return queryset.filter(search_query)
    
    def apply_date_range_filter(self, queryset, date_field, start_date, end_date):
        """
        Apply date range filtering to a queryset.
        
        Args:
            queryset: The base queryset to filter
            date_field: The date field to filter on
            start_date: Start date (string or date object)
            end_date: End date (string or date object)
            
        Returns:
            QuerySet: Filtered queryset
        """
        filters = {}
        
        if start_date:
            if isinstance(start_date, str):
                start_date = parse_date(start_date)
            if start_date:
                filters[f"{date_field}__gte"] = start_date
        
        if end_date:
            if isinstance(end_date, str):
                end_date = parse_date(end_date)
            if end_date:
                filters[f"{date_field}__lte"] = end_date
        
        if filters:
            logger.info(f"Applied date range filter on {date_field}: {filters}")
            return queryset.filter(**filters)
        
        return queryset
    
    def apply_status_filter(self, queryset, status_field, status_values):
        """
        Apply status filtering to a queryset.
        
        Args:
            queryset: The base queryset to filter
            status_field: The status field to filter on
            status_values: List of status values to include
            
        Returns:
            QuerySet: Filtered queryset
        """
        if status_values:
            if isinstance(status_values, str):
                status_values = [status_values]
            
            logger.info(f"Applied status filter on {status_field}: {status_values}")
            return queryset.filter(**{f"{status_field}__in": status_values})
        
        return queryset


class SearchFilterMixin(FilterMixin):
    """
    Mixin providing enhanced search functionality.
    
    Extends the base FilterMixin with advanced search capabilities
    including full-text search and weighted results.
    """
    search_fields = []
    
    def get_search_queryset(self, queryset):
        """
        Get search-filtered queryset based on request parameters.
        
        Args:
            queryset: The base queryset to search
            
        Returns:
            QuerySet: Search-filtered queryset
        """
        search_term = self.request.query_params.get('search', '').strip()
        if search_term and self.search_fields:
            return self.apply_search_filter(queryset, search_term, self.search_fields)
        return queryset


class DateRangeFilterMixin(FilterMixin):
    """
    Mixin providing date range filtering functionality.
    
    Allows filtering by date ranges using start_date and end_date
    query parameters.
    """
    date_field = 'created_at'
    
    def get_date_filtered_queryset(self, queryset):
        """
        Get date-range filtered queryset based on request parameters.
        
        Args:
            queryset: The base queryset to filter
            
        Returns:
            QuerySet: Date-filtered queryset
        """
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        
        return self.apply_date_range_filter(
            queryset, self.date_field, start_date, end_date
        )


class BaseFilteredViewMixin(SearchFilterMixin, DateRangeFilterMixin):
    """
    Combined mixin providing comprehensive filtering capabilities.
    
    Combines search and date range filtering with additional
    common filtering operations for a complete filtering solution.
    """
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    ordering_fields = ['created_at', 'updated_at']
    ordering = ['-created_at']
    
    def get_queryset(self):
        """
        Get the filtered queryset for the view.
        
        Applies all configured filters in the correct order for
        optimal performance.
        
        Returns:
            QuerySet: Fully filtered queryset
        """
        queryset = super().get_queryset()
        
        # Apply search filtering
        queryset = self.get_search_queryset(queryset)
        
        # Apply date range filtering
        queryset = self.get_date_filtered_queryset(queryset)
        
        # Apply any additional custom filters
        queryset = self.apply_custom_filters(queryset)
        
        return queryset
    
    def apply_custom_filters(self, queryset):
        """
        Apply custom filters specific to the view.
        
        Override this method in subclasses to add view-specific
        filtering logic.
        
        Args:
            queryset: The base queryset to filter
            
        Returns:
            QuerySet: Custom-filtered queryset
        """
        return queryset