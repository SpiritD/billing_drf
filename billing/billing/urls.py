"""
billing URL Configuration.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.2/topics/http/urls/
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
from django.conf import settings
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import (
    include,
    path,
)
from drf_yasg import openapi
from drf_yasg.views import get_schema_view
from rest_framework import permissions


version = 'v0.1'

schema_view = get_schema_view(
    openapi.Info(
        title='Billing API',
        default_version=version,
        description='Test billing service',
        terms_of_service='https://www.google.com/policies/terms/',
        license=openapi.License(name='BSD License'),
    ),
    public=True,
    permission_classes=(permissions.AllowAny,),
)


urlpatterns = [
    path('auth/', include('users.urls')),
    path('wallet/', include('wallet.urls')),
    path('admin/', admin.site.urls),
]

# Для дебага подключаем сваггер
if settings.DEBUG:
    urlpatterns += [
        # из документации https://github.com/axnsan12/drf-yasg
        url(
            r'^swagger(?P<format>\.json|\.yaml)$',
            schema_view.without_ui(cache_timeout=0),
            name='schema-json',
        ),
        url(
            r'^swagger/$',
            schema_view.with_ui('swagger', cache_timeout=0),
            name='schema-swagger-ui',
        ),
        url(
            r'^redoc/$',
            schema_view.with_ui('redoc', cache_timeout=0),
            name='schema-redoc',
        ),
    ]

    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
