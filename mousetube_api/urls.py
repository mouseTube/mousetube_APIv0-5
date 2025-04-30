"""
URL configuration for mousetube_api project.

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
from rest_framework.routers import DefaultRouter
from .views import (
    UserAPIView,
    StrainAPIView,
    SubjectAPIView,
    ProtocolAPIView,
    ExperimentAPIView,
    FileAPIView,
    FileDetailAPIView,
)
from .views import TrackPageView
from django.views.static import serve
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView
from django.contrib.admin.views.decorators import staff_member_required
import os
from django.conf import settings

router = DefaultRouter()

urlpatterns = [
    path("api/", include(router.urls)),
    path("api/user/", UserAPIView.as_view()),
    path("api/strain/", StrainAPIView.as_view()),
    path("api/subject/", SubjectAPIView.as_view()),
    path("api/protocol/", ProtocolAPIView.as_view()),
    path("api/experiment/", ExperimentAPIView.as_view()),
    path("api/file/", FileAPIView.as_view(), name="file-list"),
    path("api/file/<int:pk>/", FileDetailAPIView.as_view(), name="file-detail"),
    path("api/track-page/", TrackPageView.as_view(), name="track-page"),
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path(
        "swagger/", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"
    ),
    path(
        "admin/stats/",
        staff_member_required(serve),
        {
            "document_root": os.path.join(settings.BASE_DIR, "logs"),
            "path": "latest.html",
        },
        name="admin-stats",
    ),
    path("admin/", admin.site.urls),
]
