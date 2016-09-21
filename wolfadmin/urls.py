"""wolfadmin URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/1.10/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  url(r'^$', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  url(r'^$', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.conf.urls import url, include
    2. Add a URL to urlpatterns:  url(r'^blog/', include('blog.urls'))
"""
from django.conf.urls import url
from auth import views as auth_views
from users import views as users_views


urlpatterns = [
    # Login & Signup
    url(r'^login/$', auth_views.login, name='login'),
    url(r'^signup/$', auth_views.signup, name='signup'),
    # Dashboard
    url(r'^$', auth_views.dashboard, name="dashboard"),
    # Users
    url(r'^users/$', users_views.index, name='users'),
]
