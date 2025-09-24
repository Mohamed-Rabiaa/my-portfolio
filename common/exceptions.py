"""
Custom exception classes for the portfolio application.

This module defines custom exceptions that provide more specific error
handling and better error messages throughout the application.
"""


class PortfolioException(Exception):
    """
    Base exception class for all portfolio application exceptions.
    
    All custom exceptions in the portfolio app should inherit from this
    base class to provide consistent error handling.
    """
    def __init__(self, message="An error occurred in the portfolio application"):
        self.message = message
        super().__init__(self.message)


class ValidationError(PortfolioException):
    """
    Exception raised when data validation fails.
    
    Used for custom validation errors that are not covered by
    Django's built-in validation.
    """
    def __init__(self, field=None, message="Validation failed"):
        self.field = field
        if field:
            message = f"Validation failed for field '{field}': {message}"
        super().__init__(message)


class NotFoundError(PortfolioException):
    """
    Exception raised when a requested resource is not found.
    
    More specific than Django's Http404 and can be used in
    service layers before converting to HTTP responses.
    """
    def __init__(self, resource_type=None, identifier=None):
        if resource_type and identifier:
            message = f"{resource_type} with identifier '{identifier}' not found"
        elif resource_type:
            message = f"{resource_type} not found"
        else:
            message = "Requested resource not found"
        super().__init__(message)


class PermissionError(PortfolioException):
    """
    Exception raised when a user lacks permission for an action.
    
    Used for authorization failures in business logic.
    """
    def __init__(self, action=None, resource=None):
        if action and resource:
            message = f"Permission denied for action '{action}' on '{resource}'"
        elif action:
            message = f"Permission denied for action '{action}'"
        else:
            message = "Permission denied"
        super().__init__(message)


class BusinessLogicError(PortfolioException):
    """
    Exception raised when business logic rules are violated.
    
    Used for domain-specific errors that don't fit into other categories.
    """
    pass


# Blog-specific exceptions
class BlogPostNotFound(NotFoundError):
    """Exception raised when a blog post is not found."""
    def __init__(self, slug=None):
        super().__init__("Blog post", slug)


class BlogPostNotPublished(PortfolioException):
    """Exception raised when trying to access an unpublished blog post."""
    def __init__(self, slug=None):
        message = f"Blog post '{slug}' is not published" if slug else "Blog post is not published"
        super().__init__(message)


# Portfolio-specific exceptions
class ProjectNotFound(NotFoundError):
    """Exception raised when a project is not found."""
    def __init__(self, slug=None):
        super().__init__("Project", slug)


# Contact-specific exceptions
class InvalidContactData(ValidationError):
    """Exception raised when contact form data is invalid."""
    pass


class NewsletterSubscriptionError(PortfolioException):
    """Exception raised when newsletter subscription fails."""
    pass


class DuplicateSubscriptionError(NewsletterSubscriptionError):
    """Exception raised when trying to subscribe with an existing email."""
    def __init__(self, email):
        message = f"Email '{email}' is already subscribed to the newsletter"
        super().__init__(message)