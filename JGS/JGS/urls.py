"""JGS URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from django.urls import path, re_path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    re_path(r'^doc/$', views.DocView.as_view()),
    re_path(r'^doc/(?P<pk>\d+)/$', views.DocView.as_view()),
    re_path(r'^login/$', views.LoginView.as_view()),
    re_path(r'^register/$', views.RegisterView.as_view()),
    path('user/', views.UserView.as_view()),
    re_path(r'^group/$', views.GroupView.as_view()),
    re_path(r'^group/(?P<pk>\d+)/$', views.GroupView.as_view()),
    re_path(r'^comment/(?P<pk>\d+)/$', views.CommentView.as_view()),
    re_path(r'^group/(?P<pk>\d+)/member/$', views.GroupMemberView.as_view()),
    re_path(r'^group/(?P<pk>\d+)/member/(?P<pkk>\d+)/$', views.GroupMemberView.as_view()),
    re_path(r'^favorite/$', views.FavoriteView.as_view()),
    re_path(r'^favorite/(?P<pk>\d+)/$', views.FavoriteView.as_view()),
    re_path(r'^browse/$', views.BrowseView.as_view()),
    re_path(r'^browse/(?P<pk>\d+)/$', views.BrowseView.as_view()),
    re_path(r'^doc/user/$', views.DocUserView.as_view()),
    re_path(r'^doc/bin/$', views.DocBinView.as_view()),
]
