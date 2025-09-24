"""URL configuration for myportfolio project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
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
from django.conf.urls.static import serve
from django.views.static import serve as static_serve
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from common.versioning import get_api_version_info_view

# Custom error handlers
handler404 = 'common.error_handlers.handle_404'
handler500 = 'common.error_handlers.handle_500'
handler403 = 'common.error_handlers.handle_403'

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # API version info
    path('api/version/', get_api_version_info_view().as_view(), name='api-version-info'),
    
    # Versioned API endpoints
    path('api/v1/portfolio/', include('portfolio.urls')),
    path('api/v1/blog/', include('blog.urls')),
    path('api/v1/contact/', include('contact.urls')),
    
    # API documentation
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += [
        path('media/<path:path>', static_serve, {'document_root': settings.MEDIA_ROOT}),
    ]
