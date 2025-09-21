"""
URL configuration for myportfolio project.

This module defines the main URL routing configuration for the Django portfolio application.
It includes URL patterns for the admin interface, API endpoints, documentation, and static
file serving. The URL patterns route incoming requests to appropriate views and applications.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.2/topics/http/urls/

Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))

Author: Mohamed Rabiaa
Version: 1.0.0
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

def api_root(request):
    """
    Root API endpoint with available endpoints information.
    
    This view provides a welcome message and lists all available API endpoints
    for easy discovery and navigation. It serves as the main entry point for
    the API documentation.
    
    Args:
        request (HttpRequest): The HTTP request object
        
    Returns:
        JsonResponse: JSON response containing welcome message and endpoint list
        
    Example:
        GET / -> {
            "message": "Welcome to Mohamed Rabiaa Portfolio API",
            "version": "1.0",
            "endpoints": {
                "portfolio": "/api/portfolio/",
                "blog": "/api/blog/",
                "contact": "/api/contact/",
                "admin": "/admin/",
                "api_docs": "/api/docs/",
                "api_schema": "/api/schema/"
            }
        }
    """
    return JsonResponse({
        'message': 'Welcome to Mohamed Rabiaa Portfolio API',
        'version': '1.0',
        'endpoints': {
            'portfolio': '/api/portfolio/',    # Portfolio projects API
            'blog': '/api/blog/',              # Blog posts API
            'contact': '/api/contact/',        # Contact messages and newsletter API
            'admin': '/admin/',                # Django admin interface
            'api_docs': '/api/docs/',          # Interactive API documentation
            'api_schema': '/api/schema/'       # OpenAPI schema
        }
    })

"""
URL Patterns Configuration:
Main URL routing configuration that defines how URLs are mapped to views.
Includes API endpoints, admin interface, and documentation routes.
"""
urlpatterns = [
    # Root API endpoint - provides API overview and available endpoints
    path('', api_root, name='api-root'),
    
    # Django admin interface - for content management
    path("admin/", admin.site.urls),
    
    # API endpoints - include URL patterns from individual apps
    path('api/portfolio/', include('portfolio.urls')),  # Portfolio projects API
    path('api/blog/', include('blog.urls')),            # Blog posts API  
    path('api/contact/', include('contact.urls')),      # Contact and newsletter API
    
    # API documentation endpoints
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),           # OpenAPI schema
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'), # Interactive docs
]

"""
Development Static File Serving:
In development mode, Django serves static and media files directly.
This configuration is automatically disabled in production.
"""
# Serve media files in development
if settings.DEBUG:
    # Add URL patterns for serving uploaded media files (images, documents, etc.)
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    # Add URL patterns for serving static files (CSS, JavaScript, images)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
