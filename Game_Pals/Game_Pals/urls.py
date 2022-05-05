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
from django.conf import settings
from django.conf.urls.static import static

from django.urls import path
from django.contrib.auth.decorators import login_required
from main_app.views import MainView, HomeView, LoginView, RegisterView, UserUpdateView1, \
    UserUpdateView2, UserAddEventView, UserAddGamesView, UserDeleteGameView, UserSearchView,\
    EventDetailsView, UserDetailsView, LogoutView, FriendRequestsView, GroupCreateView, \
    UserGroupsView, GroupDetailView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', MainView.as_view(), name="main"),
    path('home/', login_required(HomeView.as_view()), name="home"),
    path('calendar', login_required(HomeView.as_view()), name="user_calendar"),
    path('add-event/', login_required(UserAddEventView.as_view()), name="user_add_event"),
    path('login/', LoginView.as_view(), name="login"),
    path('logout/', LogoutView.as_view(), name="logout"),
    path('register/', RegisterView.as_view(), name="register"),
    path('update-user-1/', login_required(UserUpdateView1.as_view()), name="user-update-1"),
    path('update-user-2/', login_required(UserUpdateView2.as_view()), name="user-update-2"),
    path('add-games/', login_required(UserAddGamesView.as_view()), name="user_add_games"),
    path('delete-games/<int:game_id>/', login_required(UserDeleteGameView.as_view()), name="user_delete_games"),
    path('user-search/', login_required(UserSearchView.as_view()), name="user_search"),
    path('event-details/<int:event_id>/', login_required(EventDetailsView.as_view()), name='event_details'),
    path('user-search/<int:user_id>/', login_required(UserDetailsView.as_view()), name='user_details'),
    path('friend-requests/', login_required(FriendRequestsView.as_view()), name='friend_requests'),
    path('create-group/', login_required(GroupCreateView.as_view()), name='create_group'),
    path('user-groups/', login_required(UserGroupsView.as_view()), name='user_groups'),
    path('group-details/<int:group_id>/', login_required(GroupDetailView.as_view()), name='group-details')
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
