"""Game_Pals URL Configuration

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
from django.contrib import admin
from django.urls import path
from django.contrib.auth.decorators import login_required
from main_app.views import TEST, MainView, HomeView, LoginView, RegisterView, UserUpdateView1, \
    UserUpdateView2

urlpatterns = [
    path('admin/', admin.site.urls),
    path('TEST/', TEST.as_view(), name="TEST"),
    path('', MainView.as_view(), name="main"),
    path('home/', login_required(HomeView.as_view()), name="home"),
    path('login/', LoginView.as_view(), name="login"),
    path('register/', RegisterView.as_view(), name="register"),
    path('update-user-1/', UserUpdateView1.as_view(), name="user-update-1"),
    path('update-user-2/', UserUpdateView2.as_view(), name="user-update-2"),
]
