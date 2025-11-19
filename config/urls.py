"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
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
from django.views.generic import TemplateView

urlpatterns = [
    path("", TemplateView.as_view(template_name="pages/home.html"), name="home"),
    path(
        "contacts/",
        TemplateView.as_view(template_name="pages/contacts.html"),
        name="contacts",
    ),
    path("docs/", TemplateView.as_view(template_name="pages/docs.html"), name="docs"),
    path(
        "docs/api/",
        TemplateView.as_view(template_name="pages/docs_api.html"),
        name="docs_api",
    ),
    path(
        "docs/api/v1/",
        TemplateView.as_view(template_name="pages/docs_api_v1.html"),
        name="docs_api_v1",
    ),
    path(
        "docs/faq/",
        TemplateView.as_view(template_name="pages/docs_faq.html"),
        name="docs_faq",
    ),
    path(
        "docs/releases/",
        TemplateView.as_view(template_name="pages/docs_releases.html"),
        name="docs_releases",
    ),
    path(
        "pricing/",
        TemplateView.as_view(template_name="pages/pricing.html"),
        name="pricing",
    ),
    path("admin/", admin.site.urls),
]
