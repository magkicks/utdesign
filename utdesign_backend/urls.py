"""
URL configuration for utdesign_backend project.

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
from django.conf.urls.static import static
from rest_framework.routers import DefaultRouter
from tasks.views import TaskViewSet  # Import your TaskViewSet from the correct app

# Create a router and register the TaskViewSet
router = DefaultRouter()
router.register(r'tasks', TaskViewSet, basename='tasks')

urlpatterns = [
    path('', include('accounts.urls', namespace='accounts')),  # Include accounts as the root namespace.
    path('admin/', admin.site.urls),
    path('proposals/', include('proposals.urls', namespace='proposals')),
    path('reports/', include('reports.urls')),
    path('tasks/', include('tasks.urls')),
    path('feedback/', include('feedback.urls')),
    path('accounts/', include('accounts.urls')),
    path('api/', include(router.urls)),  # Register API routes from the router
]

# Add this block after urlpatterns is defined
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns += [
    path('api/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]

