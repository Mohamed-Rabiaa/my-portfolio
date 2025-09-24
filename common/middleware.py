"""
Custom middleware for logging, monitoring, and request/response handling.

This module provides middleware classes for comprehensive logging of requests,
responses, performance monitoring, and error tracking across the application.
"""

import logging
import time
import json
from django.utils.deprecation import MiddlewareMixin
from django.http import JsonResponse
from django.conf import settings

# Initialize loggers
logger = logging.getLogger('django')
performance_logger = logging.getLogger('performance')


class RequestLoggingMiddleware(MiddlewareMixin):
    """
    Middleware to log all incoming requests and outgoing responses.
    
    Logs request details including method, path, user, IP address,
    and response status codes with execution times.
    """
    
    def process_request(self, request):
        """Process incoming request and log details."""
        request._start_time = time.time()
        
        # Get client IP address
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        
        # Log request details
        user = getattr(request, 'user', None)
        user_info = f"user:{user.username}" if user and user.is_authenticated else "anonymous"
        
        logger.info(
            f"REQUEST {request.method} {request.get_full_path()} "
            f"from {ip} ({user_info})"
        )
        
        # Log request body for POST/PUT/PATCH requests (excluding sensitive data)
        if request.method in ['POST', 'PUT', 'PATCH'] and hasattr(request, 'body'):
            try:
                if request.content_type == 'application/json':
                    body = json.loads(request.body.decode('utf-8'))
                    # Remove sensitive fields
                    sensitive_fields = ['password', 'token', 'secret', 'key']
                    for field in sensitive_fields:
                        if field in body:
                            body[field] = '[REDACTED]'
                    logger.debug(f"Request body: {json.dumps(body)}")
            except (json.JSONDecodeError, UnicodeDecodeError):
                logger.debug("Request body: [Non-JSON or binary data]")
    
    def process_response(self, request, response):
        """Process outgoing response and log details."""
        if hasattr(request, '_start_time'):
            execution_time = time.time() - request._start_time
            
            # Get client IP address
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            
            # Log response details
            user = getattr(request, 'user', None)
            user_info = f"user:{user.username}" if user and user.is_authenticated else "anonymous"
            
            logger.info(
                f"RESPONSE {request.method} {request.get_full_path()} "
                f"-> {response.status_code} in {execution_time:.3f}s "
                f"for {ip} ({user_info})"
            )
            
            # Log performance metrics
            performance_logger.info(
                f"{{\"method\": \"{request.method}\", \"path\": \"{request.path}\", "
                f"\"status\": {response.status_code}, \"duration\": {execution_time:.3f}, "
                f"\"user\": \"{user_info}\", \"ip\": \"{ip}\"}}"
            )
            
            # Log slow requests
            if execution_time > 1.0:  # Log requests taking more than 1 second
                logger.warning(
                    f"SLOW REQUEST: {request.method} {request.get_full_path()} "
                    f"took {execution_time:.3f}s"
                )
        
        return response
    
    def process_exception(self, request, exception):
        """Process exceptions and log error details."""
        if hasattr(request, '_start_time'):
            execution_time = time.time() - request._start_time
            
            # Get client IP address
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                ip = x_forwarded_for.split(',')[0]
            else:
                ip = request.META.get('REMOTE_ADDR')
            
            user = getattr(request, 'user', None)
            user_info = f"user:{user.username}" if user and user.is_authenticated else "anonymous"
            
            logger.error(
                f"EXCEPTION {request.method} {request.get_full_path()} "
                f"after {execution_time:.3f}s for {ip} ({user_info}): {str(exception)}",
                exc_info=True
            )
            
            performance_logger.info(
                f"{{\"method\": \"{request.method}\", \"path\": \"{request.path}\", "
                f"\"status\": \"error\", \"duration\": {execution_time:.3f}, "
                f"\"user\": \"{user_info}\", \"ip\": \"{ip}\", \"error\": \"{str(exception)}\"}}"
            )


class SecurityHeadersMiddleware(MiddlewareMixin):
    """
    Middleware to add security headers to all responses.
    
    Adds various security headers to protect against common attacks
    and improve the security posture of the application.
    """
    
    def process_response(self, request, response):
        """Add security headers to response."""
        # Content Security Policy
        if not response.get('Content-Security-Policy'):
            response['Content-Security-Policy'] = (
                "default-src 'self'; "
                "script-src 'self' 'unsafe-inline' 'unsafe-eval'; "
                "style-src 'self' 'unsafe-inline'; "
                "img-src 'self' data: https:; "
                "font-src 'self' https:; "
                "connect-src 'self';"
            )
        
        # X-Content-Type-Options
        if not response.get('X-Content-Type-Options'):
            response['X-Content-Type-Options'] = 'nosniff'
        
        # X-Frame-Options
        if not response.get('X-Frame-Options'):
            response['X-Frame-Options'] = 'DENY'
        
        # X-XSS-Protection
        if not response.get('X-XSS-Protection'):
            response['X-XSS-Protection'] = '1; mode=block'
        
        # Referrer-Policy
        if not response.get('Referrer-Policy'):
            response['Referrer-Policy'] = 'strict-origin-when-cross-origin'
        
        # Permissions-Policy
        if not response.get('Permissions-Policy'):
            response['Permissions-Policy'] = (
                "geolocation=(), microphone=(), camera=(), "
                "payment=(), usb=(), magnetometer=(), gyroscope=()"
            )
        
        return response


class APIVersionMiddleware(MiddlewareMixin):
    """
    Middleware to handle API versioning and deprecation warnings.
    
    Checks API version headers and adds deprecation warnings
    for older API versions.
    """
    
    def process_request(self, request):
        """Process API version from request headers."""
        if request.path.startswith('/api/'):
            # Get API version from header
            api_version = request.META.get('HTTP_API_VERSION', '1.0')
            request.api_version = api_version
            
            # Log API version usage
            logger.debug(f"API request with version: {api_version}")
            
            # Check for deprecated versions
            deprecated_versions = ['0.9', '0.8']
            if api_version in deprecated_versions:
                logger.warning(
                    f"Deprecated API version {api_version} used for {request.path}"
                )
    
    def process_response(self, request, response):
        """Add API version headers to response."""
        if hasattr(request, 'api_version') and request.path.startswith('/api/'):
            response['API-Version'] = request.api_version
            
            # Add deprecation warning for old versions
            deprecated_versions = ['0.9', '0.8']
            if request.api_version in deprecated_versions:
                response['Deprecation'] = 'true'
                response['Sunset'] = '2024-12-31'  # Example sunset date
                response['Link'] = '</api/v2/>; rel="successor-version"'
        
        return response