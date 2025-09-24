"""
Comprehensive error handling and monitoring system.

This module provides custom exception handlers, error tracking utilities,
and monitoring capabilities for the portfolio application.
"""

import logging
import traceback
import sys
from datetime import datetime
from django.http import JsonResponse
from django.conf import settings
from rest_framework.views import exception_handler
from rest_framework import status
from rest_framework.response import Response

# Initialize loggers
error_logger = logging.getLogger('django')
security_logger = logging.getLogger('django.security')


class ErrorTracker:
    """
    Centralized error tracking and monitoring utility.
    
    Provides methods for tracking, categorizing, and monitoring
    application errors with detailed context information.
    """
    
    @staticmethod
    def track_error(error, request=None, context=None):
        """
        Track and log an error with comprehensive context.
        
        Args:
            error: The exception or error object
            request: HTTP request object (optional)
            context: Additional context information (optional)
        """
        error_info = {
            'timestamp': datetime.now().isoformat(),
            'error_type': type(error).__name__,
            'error_message': str(error),
            'traceback': traceback.format_exc(),
        }
        
        # Add request context if available
        if request:
            error_info.update({
                'method': request.method,
                'path': request.path,
                'user': str(request.user) if hasattr(request, 'user') else 'anonymous',
                'ip_address': ErrorTracker._get_client_ip(request),
                'user_agent': request.META.get('HTTP_USER_AGENT', ''),
                'query_params': dict(request.GET),
            })
            
            # Add POST data (excluding sensitive fields)
            if request.method in ['POST', 'PUT', 'PATCH']:
                post_data = dict(request.POST) if hasattr(request, 'POST') else {}
                # Remove sensitive fields
                sensitive_fields = ['password', 'token', 'secret', 'key', 'csrf']
                for field in sensitive_fields:
                    if field in post_data:
                        post_data[field] = '[REDACTED]'
                error_info['post_data'] = post_data
        
        # Add additional context
        if context:
            error_info['context'] = context
        
        # Log the error
        error_logger.error(
            f"Error tracked: {error_info['error_type']} - {error_info['error_message']}",
            extra={'error_info': error_info},
            exc_info=True
        )
        
        return error_info
    
    @staticmethod
    def track_security_event(event_type, request, details=None):
        """
        Track security-related events and potential threats.
        
        Args:
            event_type: Type of security event
            request: HTTP request object
            details: Additional event details
        """
        security_info = {
            'timestamp': datetime.now().isoformat(),
            'event_type': event_type,
            'ip_address': ErrorTracker._get_client_ip(request),
            'user_agent': request.META.get('HTTP_USER_AGENT', ''),
            'path': request.path,
            'method': request.method,
            'user': str(request.user) if hasattr(request, 'user') else 'anonymous',
        }
        
        if details:
            security_info['details'] = details
        
        security_logger.warning(
            f"Security event: {event_type}",
            extra={'security_info': security_info}
        )
    
    @staticmethod
    def _get_client_ip(request):
        """Get client IP address from request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0].strip()
        return request.META.get('REMOTE_ADDR', '')


def custom_exception_handler(exc, context):
    """
    Custom exception handler for REST framework.
    
    Provides comprehensive error handling with logging,
    monitoring, and user-friendly error responses.
    """
    # Get the standard error response
    response = exception_handler(exc, context)
    
    # Get request from context
    request = context.get('request')
    
    # Track the error
    error_info = ErrorTracker.track_error(exc, request, {
        'view': context.get('view').__class__.__name__ if context.get('view') else None,
        'args': context.get('args', []),
        'kwargs': context.get('kwargs', {}),
    })
    
    # Customize response based on error type
    if response is not None:
        custom_response_data = {
            'error': True,
            'error_type': type(exc).__name__,
            'message': 'An error occurred while processing your request.',
            'timestamp': datetime.now().isoformat(),
        }
        
        # Add specific error messages for different status codes
        if response.status_code == 400:
            custom_response_data['message'] = 'Invalid request data provided.'
            if hasattr(response, 'data') and response.data:
                custom_response_data['details'] = response.data
        elif response.status_code == 401:
            custom_response_data['message'] = 'Authentication required.'
        elif response.status_code == 403:
            custom_response_data['message'] = 'Permission denied.'
            # Track potential security event
            ErrorTracker.track_security_event('permission_denied', request, {
                'attempted_action': context.get('view').__class__.__name__
            })
        elif response.status_code == 404:
            custom_response_data['message'] = 'The requested resource was not found.'
        elif response.status_code == 429:
            custom_response_data['message'] = 'Too many requests. Please try again later.'
            # Track potential security event
            ErrorTracker.track_security_event('rate_limit_exceeded', request)
        elif response.status_code >= 500:
            custom_response_data['message'] = 'Internal server error. Please try again later.'
            if settings.DEBUG:
                custom_response_data['debug_info'] = {
                    'error_type': type(exc).__name__,
                    'error_message': str(exc),
                }
        
        # Add error ID for tracking
        custom_response_data['error_id'] = f"ERR_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{id(exc)}"
        
        response.data = custom_response_data
    
    return response


def handle_404(request, exception):
    """Custom 404 error handler."""
    ErrorTracker.track_error(exception, request, {'error_type': '404_not_found'})
    
    return JsonResponse({
        'error': True,
        'error_type': 'NotFound',
        'message': 'The requested page or resource was not found.',
        'timestamp': datetime.now().isoformat(),
        'path': request.path,
    }, status=404)


def handle_500(request):
    """Custom 500 error handler."""
    exc_type, exc_value, exc_traceback = sys.exc_info()
    if exc_value:
        ErrorTracker.track_error(exc_value, request, {'error_type': '500_server_error'})
    
    return JsonResponse({
        'error': True,
        'error_type': 'InternalServerError',
        'message': 'An internal server error occurred. Please try again later.',
        'timestamp': datetime.now().isoformat(),
    }, status=500)


def handle_403(request, exception):
    """Custom 403 error handler."""
    ErrorTracker.track_security_event('permission_denied_403', request, {
        'exception': str(exception)
    })
    
    return JsonResponse({
        'error': True,
        'error_type': 'PermissionDenied',
        'message': 'You do not have permission to access this resource.',
        'timestamp': datetime.now().isoformat(),
    }, status=403)


class ErrorMonitoringMiddleware:
    """
    Middleware for monitoring and tracking application errors.
    
    Provides real-time error monitoring, performance tracking,
    and security event detection.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        response = self.get_response(request)
        
        # Monitor for potential security issues
        self._monitor_security_events(request, response)
        
        return response
    
    def process_exception(self, request, exception):
        """Process unhandled exceptions."""
        ErrorTracker.track_error(exception, request, {
            'middleware': 'ErrorMonitoringMiddleware',
            'unhandled': True
        })
        return None
    
    def _monitor_security_events(self, request, response):
        """Monitor for potential security events."""
        # Monitor for suspicious patterns
        if response.status_code == 404 and self._is_suspicious_path(request.path):
            ErrorTracker.track_security_event('suspicious_path_access', request, {
                'path': request.path,
                'status_code': response.status_code
            })
        
        # Monitor for potential brute force attempts
        if response.status_code == 401 and request.path.startswith('/api/auth/'):
            ErrorTracker.track_security_event('authentication_failure', request, {
                'path': request.path,
                'status_code': response.status_code
            })
    
    def _is_suspicious_path(self, path):
        """Check if path looks suspicious."""
        suspicious_patterns = [
            '/admin/', '/wp-admin/', '/.env', '/config/', '/backup/',
            '/phpmyadmin/', '/mysql/', '/database/', '/.git/',
            '/shell.php', '/cmd.php', '/eval.php'
        ]
        return any(pattern in path.lower() for pattern in suspicious_patterns)


# Custom exception classes
class ValidationError(Exception):
    """Custom validation error."""
    pass


class BusinessLogicError(Exception):
    """Custom business logic error."""
    pass


class ExternalServiceError(Exception):
    """Error when external service fails."""
    pass