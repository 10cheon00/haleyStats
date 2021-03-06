"""haley_gg URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.1/topics/http/urls/
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
import debug_toolbar

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from haley_gg import views

urlpatterns = [
    path('__debug__/', include(debug_toolbar.urls)),
    path('', views.main_page, name="main_page"),
    path('admin/', admin.site.urls),
    path('stats/', include("haley_gg.apps.stats.urls", namespace="stats")),
]
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
# ???
