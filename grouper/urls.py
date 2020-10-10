"""grouper URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.conf.urls import url
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import path, include
from rest_framework import routers

from chat import views as chat_views
from grouper import settings
from groups import views as groups_views
from posts import views as posts_views
from users import views as users_views

router = routers.SimpleRouter()
router.register(r'users', users_views.UsersViewSet)
router.register(r'groups', groups_views.GroupViewSet)
router.register(r'posts', posts_views.PostsViewSet)
router.register(r'chat', chat_views.ChatViewSet)

urlpatterns = [
                  path('', include(router.urls)),
                  path('admin/', admin.site.urls),
                  url(r'^login/', users_views.CustomAuthToken.as_view()),
              ]
