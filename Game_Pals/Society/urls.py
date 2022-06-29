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

from .views import DeleteFriendship, FriendCalendarView, FriendRequestsView, UserDetailsView, UserPalsView, UserSearchView


app_name = "society"
urlpatterns = [
    path('user-search/', UserSearchView.as_view(), name="user_search"),
    path('user-search/<int:user_id>/', UserDetailsView.as_view(), name='user_details'),
    path('friend-requests/', FriendRequestsView.as_view(), name='friend_requests'),
    path('pals-list/', UserPalsView.as_view(), name='user_pals'),
    path('pals-list/<int:pk>/delete', DeleteFriendship.as_view(), name='delete_friendship'),
    path('friend-calendar/<int:friend_id>/', FriendCalendarView.as_view(), name='friend_calendar'),
    path('friend-calendar/<int:friend_id>/calendar', FriendCalendarView.as_view(),
         name="friend_calendar_details"),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
