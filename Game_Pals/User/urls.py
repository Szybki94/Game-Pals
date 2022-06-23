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

from .views import EventDeleteView, EventDetailsView, HomeView, UserAddGamesView, UserDeleteGameView, UserAddEventView


app_name = "user"
urlpatterns = [
    path('home/', HomeView.as_view(), name="home-view"),
    path('calendar', HomeView.as_view(), name="user_calendar"),
    path('add-event/', UserAddEventView.as_view(), name="user_add_event"),
    path('event-details/<int:event_id>/', EventDetailsView.as_view(), name='event_details'),
    path('event-delete/<int:event_id>/', EventDeleteView.as_view(), name='user_delete_event_confirm'),
    path('add-games/', UserAddGamesView.as_view(), name="user_add_games"),
    path('delete-games/<int:game_id>/', UserDeleteGameView.as_view(), name="user_delete_games"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
