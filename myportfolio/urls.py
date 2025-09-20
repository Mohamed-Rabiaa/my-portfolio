"""
URL Configuration for MyPortfolio Project

This module defines the main URL routing configuration for the MyPortfolio project,
organizing API endpoints, admin interface, documentation, and static file serving.
The configuration supports a RESTful API structure with comprehensive documentation.

URL Structure:
- Root API endpoint with navigation information
- Admin interface for content management
- Modular API endpoints for each application
- Interactive API documentation with Swagger UI
- Development-only static and media file serving

API Endpoints:
- /api/portfolio/ - Portfolio projects and skills management
- /api/blog/ - Blog posts, categories, and tags
- /api/contact/ - Contact messages and newsletter subscriptions
- /admin/ - Django admin interface
- /api/docs/ - Interactive API documentation (Swagger UI)
- /api/schema/ - OpenAPI schema endpoint

Features:
- RESTful API design with consistent URL patterns
- Comprehensive API documentation with drf-spectacular
- Modular URL configuration with app-specific routing
- Development-friendly static file serving
- Root endpoint with API navigation information

For more information on Django URL configuration, see:
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
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

def api_root(request):
    """
    Root API endpoint providing navigation and project information.
    
    This view serves as the main entry point for the Portfolio API, providing
    a welcome message, version information, and a comprehensive list of
    available endpoints for easy API discovery and navigation.
    
    Args:
        request: The HTTP request object
        
    Returns:
        JsonResponse: JSON response containing:
            - message: Welcome message with project name
            - version: Current API version
            - endpoints: Dictionary of available API endpoints with descriptions
            
    Response Format:
        {
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
            'portfolio': '/api/portfolio/',
            'blog': '/api/blog/',
            'contact': '/api/contact/',
            'admin': '/admin/',
            'api_docs': '/api/docs/',
            'api_schema': '/api/schema/'
        }
    })

urlpatterns = [
    path('', api_root, name='api-root'),
    path("admin/", admin.site.urls),
    
    # API endpoints
    path('api/portfolio/', include('portfolio.urls')),
    path('api/blog/', include('blog.urls')),
    path('api/contact/', include('contact.urls')),
    
    # API documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
