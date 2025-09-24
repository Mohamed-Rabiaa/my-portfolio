"""
API versioning and deprecation handling utilities.

This module provides comprehensive API versioning support including:
- Version-aware URL routing
- Deprecation warnings and handling
- Version compatibility checks
- Migration utilities
"""

import logging
import warnings
from datetime import datetime, timedelta
from django.conf import settings
from django.http import JsonResponse
from rest_framework.versioning import URLPathVersioning
from rest_framework.response import Response
from rest_framework import status
from functools import wraps

logger = logging.getLogger('api.versioning')


class APIVersioning(URLPathVersioning):
    """
    Custom API versioning class that extends DRF's URLPathVersioning.
    
    Provides enhanced version handling with deprecation warnings,
    compatibility checks, and detailed logging.
    """
    
    allowed_versions = ['v1', 'v2']
    default_version = 'v1'
    version_param = 'version'
    
    def determine_version(self, request, *args, **kwargs):
        """
        Determine the API version from the request.
        
        Logs version usage and handles deprecation warnings.
        """
        version = super().determine_version(request, *args, **kwargs)
        
        # Log version usage
        logger.info(
            f"API version {version} requested",
            extra={
                'version': version,
                'path': request.path,
                'method': request.method,
                'user_agent': request.META.get('HTTP_USER_AGENT', 'Unknown'),
                'ip_address': self._get_client_ip(request)
            }
        )
        
        # Check for deprecated versions
        if self._is_version_deprecated(version):
            self._handle_deprecated_version(request, version)
        
        return version
    
    def _get_client_ip(self, request):
        """Extract client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')
    
    def _is_version_deprecated(self, version):
        """Check if a version is deprecated."""
        deprecated_versions = getattr(settings, 'DEPRECATED_API_VERSIONS', {})
        return version in deprecated_versions
    
    def _handle_deprecated_version(self, request, version):
        """Handle deprecated version usage."""
        deprecated_versions = getattr(settings, 'DEPRECATED_API_VERSIONS', {})
        deprecation_info = deprecated_versions.get(version, {})
        
        sunset_date = deprecation_info.get('sunset_date')
        replacement_version = deprecation_info.get('replacement_version', 'latest')
        
        # Log deprecation usage
        logger.warning(
            f"Deprecated API version {version} used",
            extra={
                'version': version,
                'sunset_date': sunset_date,
                'replacement_version': replacement_version,
                'path': request.path,
                'ip_address': self._get_client_ip(request)
            }
        )
        
        # Add deprecation warning to response headers
        if hasattr(request, '_deprecation_warnings'):
            request._deprecation_warnings.append({
                'version': version,
                'sunset_date': sunset_date,
                'replacement_version': replacement_version
            })
        else:
            request._deprecation_warnings = [{
                'version': version,
                'sunset_date': sunset_date,
                'replacement_version': replacement_version
            }]


def deprecated_api(sunset_date=None, replacement_version=None, message=None):
    """
    Decorator to mark API endpoints as deprecated.
    
    Args:
        sunset_date (str): Date when the API will be removed (YYYY-MM-DD)
        replacement_version (str): Version that should be used instead
        message (str): Custom deprecation message
    """
    def decorator(func):
        @wraps(func)
        def wrapper(self, request, *args, **kwargs):
            # Create deprecation warning
            warning_message = message or f"API endpoint {request.path} is deprecated"
            if sunset_date:
                warning_message += f" and will be removed on {sunset_date}"
            if replacement_version:
                warning_message += f". Use version {replacement_version} instead"
            
            # Log deprecation usage
            logger.warning(
                f"Deprecated API endpoint accessed: {request.path}",
                extra={
                    'path': request.path,
                    'method': request.method,
                    'sunset_date': sunset_date,
                    'replacement_version': replacement_version,
                    'ip_address': APIVersioning()._get_client_ip(request)
                }
            )
            
            # Execute the original function
            response = func(self, request, *args, **kwargs)
            
            # Add deprecation headers to response
            if hasattr(response, 'headers'):
                response.headers['Deprecation'] = 'true'
                if sunset_date:
                    response.headers['Sunset'] = sunset_date
                if replacement_version:
                    response.headers['X-API-Replacement-Version'] = replacement_version
                response.headers['Warning'] = f'299 - "{warning_message}"'
            
            return response
        return wrapper
    return decorator


class VersionCompatibilityMixin:
    """
    Mixin to add version compatibility checks to API views.
    """
    
    min_version = None
    max_version = None
    
    def dispatch(self, request, *args, **kwargs):
        """Check version compatibility before processing request."""
        version = getattr(request, 'version', None)
        
        if not self._is_version_compatible(version):
            return self._version_not_supported_response(version)
        
        return super().dispatch(request, *args, **kwargs)
    
    def _is_version_compatible(self, version):
        """Check if the requested version is compatible."""
        if not version:
            return True
        
        # Extract version number for comparison
        try:
            version_num = int(version.replace('v', ''))
        except (ValueError, AttributeError):
            return False
        
        if self.min_version:
            min_num = int(self.min_version.replace('v', ''))
            if version_num < min_num:
                return False
        
        if self.max_version:
            max_num = int(self.max_version.replace('v', ''))
            if version_num > max_num:
                return False
        
        return True
    
    def _version_not_supported_response(self, version):
        """Return response for unsupported version."""
        logger.error(
            f"Unsupported API version {version} requested",
            extra={
                'version': version,
                'path': self.request.path,
                'supported_versions': getattr(settings, 'ALLOWED_API_VERSIONS', [])
            }
        )
        
        return JsonResponse({
            'error': 'Version not supported',
            'version': version,
            'supported_versions': getattr(settings, 'ALLOWED_API_VERSIONS', []),
            'message': f'API version {version} is not supported by this endpoint'
        }, status=status.HTTP_400_BAD_REQUEST)


def get_api_version_info_view():
    """Factory function to create APIVersionInfoView avoiding circular imports."""
    from rest_framework.views import APIView
    
    class APIVersionInfoView(APIView):
        """
        View to provide information about available API versions.
        """
        
        def get(self, request):
            """Return information about available API versions."""
            versions_info = {
                'current_version': getattr(settings, 'DEFAULT_API_VERSION', 'v1'),
                'supported_versions': getattr(settings, 'ALLOWED_API_VERSIONS', ['v1']),
                'deprecated_versions': getattr(settings, 'DEPRECATED_API_VERSIONS', {}),
                'version_info': {
                    'v1': {
                        'status': 'stable',
                        'release_date': '2024-01-01',
                        'features': ['Basic portfolio API', 'Blog management', 'Contact forms']
                    },
                    'v2': {
                        'status': 'beta',
                        'release_date': '2024-06-01',
                        'features': ['Enhanced portfolio API', 'Advanced blog features', 'Analytics']
                    }
                }
            }
            
            logger.info(
                "API version info requested",
                extra={
                    'path': request.path,
                    'ip_address': APIVersioning()._get_client_ip(request)
                }
            )
            
            return Response(versions_info)
    
    return APIVersionInfoView


def version_aware_url(pattern, view, versions=None, name=None):
    """
    Create version-aware URL patterns.
    
    Args:
        pattern (str): URL pattern
        view: View class or function
        versions (list): List of supported versions
        name (str): URL name
    
    Returns:
        list: List of URL patterns for each version
    """
    if versions is None:
        versions = getattr(settings, 'ALLOWED_API_VERSIONS', ['v1'])
    
    patterns = []
    for version in versions:
        versioned_pattern = f'{version}/{pattern}'
        versioned_name = f'{name}_{version}' if name else None
        patterns.append(path(versioned_pattern, view, name=versioned_name))
    
    return patterns


class VersionMigrationHelper:
    """
    Helper class for managing API version migrations.
    """
    
    @staticmethod
    def migrate_request_data(data, from_version, to_version):
        """
        Migrate request data between API versions.
        
        Args:
            data (dict): Request data
            from_version (str): Source version
            to_version (str): Target version
        
        Returns:
            dict: Migrated data
        """
        logger.info(
            f"Migrating request data from {from_version} to {to_version}",
            extra={
                'from_version': from_version,
                'to_version': to_version,
                'data_keys': list(data.keys()) if isinstance(data, dict) else 'non-dict'
            }
        )
        
        # Add migration logic here based on version differences
        migrated_data = data.copy() if isinstance(data, dict) else data
        
        # Example migration logic (customize based on your API changes)
        if from_version == 'v1' and to_version == 'v2':
            # Handle v1 to v2 migration
            if isinstance(migrated_data, dict):
                # Example: rename fields, transform data structures
                if 'old_field' in migrated_data:
                    migrated_data['new_field'] = migrated_data.pop('old_field')
        
        return migrated_data
    
    @staticmethod
    def migrate_response_data(data, from_version, to_version):
        """
        Migrate response data between API versions.
        
        Args:
            data (dict): Response data
            from_version (str): Source version
            to_version (str): Target version
        
        Returns:
            dict: Migrated data
        """
        logger.info(
            f"Migrating response data from {from_version} to {to_version}",
            extra={
                'from_version': from_version,
                'to_version': to_version
            }
        )
        
        # Add migration logic here based on version differences
        migrated_data = data.copy() if isinstance(data, dict) else data
        
        # Example migration logic (customize based on your API changes)
        if from_version == 'v2' and to_version == 'v1':
            # Handle v2 to v1 migration (backward compatibility)
            if isinstance(migrated_data, dict):
                # Example: remove new fields, transform data structures
                migrated_data.pop('new_field', None)
        
        return migrated_data