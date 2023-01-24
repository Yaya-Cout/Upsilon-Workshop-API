"""workshop URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/4.1/topics/http/urls/
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
from django.urls import path

from django.urls import include
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from rest_framework import routers
from workshop.api import views

from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, \
    SpectacularSwaggerView

urlpatterns = [
    path("admin/", admin.site.urls),
]

router = routers.DefaultRouter()
# We don't want conflict with UserViewSet and RegisterViewSet
router.register(r'users', views.UserViewSet, basename='user')
router.register(r'groups', views.GroupViewSet, basename='group')
router.register(r'scripts', views.ScriptViewSet, basename='script')
router.register(r'ratings', views.RatingViewSet, basename='rating')
router.register(r'os', views.OSViewSet, basename='os')
router.register(r'tags', views.TagViewSet, basename='tag')
router.register(r'register', views.RegisterViewSet, basename='register')

urlpatterns += [
    path('', include(router.urls)),
    path('api-auth/', include(
        'rest_framework.urls',
        namespace='rest_framework'
        )
    )
]

# OpenAPI
urlpatterns += [
    # Schema View
    path('docs/', SpectacularAPIView.as_view(), name='schema'),

    # Swagger and ReDoc
    path('docs/swagger-ui/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
    path('docs/redoc/', SpectacularRedocView.as_view(url_name='schema'), name='redoc'),
]

urlpatterns += staticfiles_urlpatterns()
