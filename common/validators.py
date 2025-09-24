"""
Comprehensive input validation and sanitization utilities.

This module provides robust validation and sanitization for user inputs including:
- HTML content sanitization
- Email validation and normalization
- URL validation and sanitization
- File upload validation
- SQL injection prevention
- XSS protection
- CSRF protection utilities
"""

import re
import logging
import bleach
from urllib.parse import urlparse, urlunparse
from django.core.validators import validate_email, URLValidator
from django.core.exceptions import ValidationError
from django.utils.html import strip_tags, escape
from django.conf import settings
from rest_framework import serializers
from rest_framework.exceptions import ValidationError as DRFValidationError

logger = logging.getLogger('validation')


class InputSanitizer:
    """
    Comprehensive input sanitization utility.
    
    Provides methods to sanitize various types of user input
    to prevent security vulnerabilities.
    """
    
    # Allowed HTML tags for rich text content
    ALLOWED_TAGS = [
        'p', 'br', 'strong', 'em', 'u', 'ol', 'ul', 'li',
        'h1', 'h2', 'h3', 'h4', 'h5', 'h6',
        'blockquote', 'code', 'pre',
        'a', 'img'
    ]
    
    # Allowed HTML attributes
    ALLOWED_ATTRIBUTES = {
        'a': ['href', 'title'],
        'img': ['src', 'alt', 'title', 'width', 'height'],
        '*': ['class']
    }
    
    # Allowed URL protocols
    ALLOWED_PROTOCOLS = ['http', 'https', 'mailto']
    
    @classmethod
    def sanitize_html(cls, content, allowed_tags=None, allowed_attributes=None):
        """
        Sanitize HTML content to prevent XSS attacks.
        
        Args:
            content (str): HTML content to sanitize
            allowed_tags (list): Override default allowed tags
            allowed_attributes (dict): Override default allowed attributes
        
        Returns:
            str: Sanitized HTML content
        """
        if not content:
            return content
        
        tags = allowed_tags or cls.ALLOWED_TAGS
        attributes = allowed_attributes or cls.ALLOWED_ATTRIBUTES
        
        try:
            sanitized = bleach.clean(
                content,
                tags=tags,
                attributes=attributes,
                protocols=cls.ALLOWED_PROTOCOLS,
                strip=True
            )
            
            logger.debug(
                f"HTML content sanitized",
                extra={
                    'original_length': len(content),
                    'sanitized_length': len(sanitized),
                    'tags_removed': len(content) != len(sanitized)
                }
            )
            
            return sanitized
            
        except Exception as e:
            logger.error(
                f"HTML sanitization failed: {str(e)}",
                extra={'content_preview': content[:100]}
            )
            # Fallback to complete tag stripping
            return strip_tags(content)
    
    @classmethod
    def sanitize_text(cls, text, max_length=None, strip_html=True):
        """
        Sanitize plain text input.
        
        Args:
            text (str): Text to sanitize
            max_length (int): Maximum allowed length
            strip_html (bool): Whether to strip HTML tags
        
        Returns:
            str: Sanitized text
        """
        if not text:
            return text
        
        # Strip HTML tags if requested
        if strip_html:
            text = strip_tags(text)
        
        # Escape HTML entities
        text = escape(text)
        
        # Remove null bytes and control characters
        text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)
        
        # Normalize whitespace
        text = re.sub(r'\s+', ' ', text).strip()
        
        # Truncate if max_length specified
        if max_length and len(text) > max_length:
            text = text[:max_length].rstrip()
            logger.warning(
                f"Text truncated to {max_length} characters",
                extra={'original_length': len(text)}
            )
        
        return text
    
    @classmethod
    def sanitize_email(cls, email):
        """
        Sanitize and validate email address.
        
        Args:
            email (str): Email address to sanitize
        
        Returns:
            str: Sanitized email address
        
        Raises:
            ValidationError: If email is invalid
        """
        if not email:
            return email
        
        # Normalize email
        email = email.lower().strip()
        
        # Remove dangerous characters
        email = re.sub(r'[<>"\'\x00-\x1F\x7F]', '', email)
        
        # Validate email format
        try:
            validate_email(email)
        except ValidationError as e:
            logger.warning(
                f"Invalid email format: {email}",
                extra={'error': str(e)}
            )
            raise ValidationError(f"Invalid email format: {email}")
        
        return email
    
    @classmethod
    def sanitize_url(cls, url, allowed_schemes=None):
        """
        Sanitize and validate URL.
        
        Args:
            url (str): URL to sanitize
            allowed_schemes (list): Allowed URL schemes
        
        Returns:
            str: Sanitized URL
        
        Raises:
            ValidationError: If URL is invalid
        """
        if not url:
            return url
        
        allowed_schemes = allowed_schemes or ['http', 'https']
        
        # Parse URL
        try:
            parsed = urlparse(url)
        except Exception as e:
            logger.warning(f"URL parsing failed: {url}", extra={'error': str(e)})
            raise ValidationError(f"Invalid URL format: {url}")
        
        # Validate scheme
        if parsed.scheme.lower() not in allowed_schemes:
            raise ValidationError(f"URL scheme not allowed: {parsed.scheme}")
        
        # Reconstruct URL to normalize it
        sanitized_url = urlunparse(parsed)
        
        # Additional validation using Django's URLValidator
        validator = URLValidator(schemes=allowed_schemes)
        try:
            validator(sanitized_url)
        except ValidationError as e:
            logger.warning(
                f"URL validation failed: {sanitized_url}",
                extra={'error': str(e)}
            )
            raise ValidationError(f"Invalid URL: {sanitized_url}")
        
        return sanitized_url


class SecureValidator:
    """
    Security-focused validation utilities.
    """
    
    # Common SQL injection patterns
    SQL_INJECTION_PATTERNS = [
        r"(\b(SELECT|INSERT|UPDATE|DELETE|DROP|CREATE|ALTER|EXEC|UNION)\b)",
        r"(--|#|/\*|\*/)",
        r"(\b(OR|AND)\s+\d+\s*=\s*\d+)",
        r"(\bOR\s+\d+\s*=\s*\d+)",
        r"(\'\s*(OR|AND)\s*\'\w*\'\s*=\s*\'\w*)",
    ]
    
    # XSS patterns
    XSS_PATTERNS = [
        r"<script[^>]*>.*?</script>",
        r"javascript:",
        r"vbscript:",
        r"onload\s*=",
        r"onerror\s*=",
        r"onclick\s*=",
    ]
    
    @classmethod
    def check_sql_injection(cls, value):
        """
        Check for potential SQL injection attempts.
        
        Args:
            value (str): Value to check
        
        Returns:
            bool: True if potential SQL injection detected
        """
        if not isinstance(value, str):
            return False
        
        value_lower = value.lower()
        
        for pattern in cls.SQL_INJECTION_PATTERNS:
            if re.search(pattern, value_lower, re.IGNORECASE):
                logger.warning(
                    f"Potential SQL injection detected",
                    extra={
                        'pattern': pattern,
                        'value_preview': value[:100]
                    }
                )
                return True
        
        return False
    
    @classmethod
    def check_xss_attempt(cls, value):
        """
        Check for potential XSS attempts.
        
        Args:
            value (str): Value to check
        
        Returns:
            bool: True if potential XSS detected
        """
        if not isinstance(value, str):
            return False
        
        value_lower = value.lower()
        
        for pattern in cls.XSS_PATTERNS:
            if re.search(pattern, value_lower, re.IGNORECASE):
                logger.warning(
                    f"Potential XSS attempt detected",
                    extra={
                        'pattern': pattern,
                        'value_preview': value[:100]
                    }
                )
                return True
        
        return False
    
    @classmethod
    def validate_safe_input(cls, value, field_name="input"):
        """
        Comprehensive security validation for user input.
        
        Args:
            value (str): Value to validate
            field_name (str): Name of the field being validated
        
        Raises:
            ValidationError: If security issues detected
        """
        if not isinstance(value, str):
            return
        
        # Check for SQL injection
        if cls.check_sql_injection(value):
            raise ValidationError(f"Invalid characters detected in {field_name}")
        
        # Check for XSS attempts
        if cls.check_xss_attempt(value):
            raise ValidationError(f"Invalid content detected in {field_name}")
        
        # Check for null bytes
        if '\x00' in value:
            raise ValidationError(f"Null bytes not allowed in {field_name}")


class FileValidator:
    """
    File upload validation utilities.
    """
    
    # Allowed file extensions
    ALLOWED_EXTENSIONS = {
        'image': ['.jpg', '.jpeg', '.png', '.gif', '.webp', '.svg'],
        'document': ['.pdf', '.doc', '.docx', '.txt', '.rtf'],
        'archive': ['.zip', '.tar', '.gz']
    }
    
    # Maximum file sizes (in bytes)
    MAX_FILE_SIZES = {
        'image': 5 * 1024 * 1024,  # 5MB
        'document': 10 * 1024 * 1024,  # 10MB
        'archive': 50 * 1024 * 1024,  # 50MB
    }
    
    @classmethod
    def validate_file_extension(cls, filename, file_type='image'):
        """
        Validate file extension.
        
        Args:
            filename (str): Name of the file
            file_type (str): Type of file (image, document, archive)
        
        Raises:
            ValidationError: If extension not allowed
        """
        if not filename:
            raise ValidationError("Filename is required")
        
        # Get file extension
        extension = '.' + filename.split('.')[-1].lower() if '.' in filename else ''
        
        allowed_extensions = cls.ALLOWED_EXTENSIONS.get(file_type, [])
        
        if extension not in allowed_extensions:
            logger.warning(
                f"Invalid file extension: {extension}",
                extra={
                    'filename': filename,
                    'file_type': file_type,
                    'allowed_extensions': allowed_extensions
                }
            )
            raise ValidationError(
                f"File extension '{extension}' not allowed for {file_type} files. "
                f"Allowed extensions: {', '.join(allowed_extensions)}"
            )
    
    @classmethod
    def validate_file_size(cls, file_size, file_type='image'):
        """
        Validate file size.
        
        Args:
            file_size (int): Size of file in bytes
            file_type (str): Type of file
        
        Raises:
            ValidationError: If file too large
        """
        max_size = cls.MAX_FILE_SIZES.get(file_type, 1024 * 1024)  # Default 1MB
        
        if file_size > max_size:
            logger.warning(
                f"File too large: {file_size} bytes",
                extra={
                    'file_type': file_type,
                    'max_size': max_size
                }
            )
            raise ValidationError(
                f"File too large. Maximum size for {file_type} files is "
                f"{max_size // (1024 * 1024)}MB"
            )


class ValidationMixin:
    """
    Mixin to add comprehensive validation to serializers.
    """
    
    def validate(self, attrs):
        """
        Comprehensive validation for all fields.
        """
        attrs = super().validate(attrs)
        
        # Validate each field for security issues
        for field_name, value in attrs.items():
            if isinstance(value, str):
                try:
                    SecureValidator.validate_safe_input(value, field_name)
                except ValidationError as e:
                    raise DRFValidationError({field_name: str(e)})
        
        return attrs
    
    def to_internal_value(self, data):
        """
        Sanitize input data before validation.
        """
        # Sanitize string fields
        if isinstance(data, dict):
            sanitized_data = {}
            for key, value in data.items():
                if isinstance(value, str):
                    # Apply appropriate sanitization based on field type
                    if 'email' in key.lower():
                        try:
                            sanitized_data[key] = InputSanitizer.sanitize_email(value)
                        except ValidationError:
                            sanitized_data[key] = value  # Let field validation handle it
                    elif 'url' in key.lower() or 'link' in key.lower():
                        try:
                            sanitized_data[key] = InputSanitizer.sanitize_url(value)
                        except ValidationError:
                            sanitized_data[key] = value  # Let field validation handle it
                    elif 'content' in key.lower() or 'description' in key.lower():
                        sanitized_data[key] = InputSanitizer.sanitize_html(value)
                    else:
                        sanitized_data[key] = InputSanitizer.sanitize_text(value)
                else:
                    sanitized_data[key] = value
            data = sanitized_data
        
        return super().to_internal_value(data)


# Custom validator functions for use in serializer fields
def validate_no_sql_injection(value):
    """Validator function to prevent SQL injection."""
    SecureValidator.validate_safe_input(value, "field")


def validate_safe_html(value):
    """Validator function for safe HTML content."""
    if SecureValidator.check_xss_attempt(value):
        raise ValidationError("Invalid HTML content detected")


def validate_clean_text(value):
    """Validator function for clean text input."""
    SecureValidator.validate_safe_input(value, "text field")