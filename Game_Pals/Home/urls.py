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
from django.conf import settings
from django.conf.urls.static import static

from django.urls import path

from .views import MainView, LoginView, RegisterView, UserUpdateView1, UserUpdateView2, LogoutView


app_name = "home"
urlpatterns = [
    path('', MainView.as_view(), name="main"),
    path('login/', LoginView.as_view(), name="login"),
    path('register/', RegisterView.as_view(), name="register"),
    path('update-user-1/', UserUpdateView1.as_view(), name="user-update-1"),
    path('update-user-2/', UserUpdateView2.as_view(), name="user-update-2"),
    path('logout/', LogoutView.as_view(), name="logout"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
