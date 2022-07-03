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


from .views import AddMemberView, DeleteComment, DeleteEventComment, GroupEventDeleteView, GroupEventDetailsView,\
    GroupAddEventView, GroupCreateView, GroupDetailView, MemberUpdateView, UserGroupsView


app_name = "group"
urlpatterns = [
    path('create-group/', GroupCreateView.as_view(), name='create_group'),
    path('user-groups/', UserGroupsView.as_view(), name='user_groups'),
    path('group-details/<int:group_id>/', GroupDetailView.as_view(), name='group_details'),
    path('group-details/<int:group_id>/calendar', GroupDetailView.as_view(), name="group_calendar"),
    path('group-details/<int:group_id>/add-event/', GroupAddEventView.as_view(),
         name="group_add_event"),
    path('group-details/<int:group_id>/event-details/<int:event_id>/',
         GroupEventDetailsView.as_view(), name="group_event_details"),
    path('group-details/<int:group_id>/event-delete/<int:event_id>/', GroupEventDeleteView.as_view(),
         name='group_delete_event_confirm'),
    path('group-details/<int:group_id>/add-member/', AddMemberView.as_view(), name='add_member'),
    path('group-details/<int:group_id>/member/<int:member_id>', MemberUpdateView.as_view(), name='update_member'),
    path('group-details/<int:group_id>/comment/<int:pk>/delete', DeleteComment.as_view(), name='delete_comment'),
    path('group-details/<int:group_id>/event-details/<int:event_id>/comment/<int:pk>/delete',
         DeleteEventComment.as_view(), name='delete_event_comment'),
]

urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
