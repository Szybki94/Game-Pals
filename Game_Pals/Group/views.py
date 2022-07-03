from django.db import transaction
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.shortcuts import redirect, render
from django.utils import timezone
from django.utils.safestring import mark_safe
from django.urls import reverse_lazy
from django.views import View
from django.views.generic import CreateView, DeleteView, ListView


# MODELS
from .models import Comment, Group, UserGroup
from User.models import Event


# PYTHON MODULES
from datetime import date, datetime, timedelta


# FORMS
from .forms import CreateGroupForm, GroupCommentForm
from User.forms import EventDeleteForm, UserAddEventForm


# MY UTILS
import calendar
from .utils import GroupCalendar

# MIXINS


# CALENDAR FUNCTIONS
def get_date(req_day):
    if req_day:
        year, month = (int(x) for x in req_day.split('-'))
        return date(year, month, day=1)
    return datetime.today()


def prev_month(d):
    first = d.replace(day=1)
    prev_month = first - timedelta(days=1)
    month = 'month=' + str(prev_month.year) + '-' + str(prev_month.month)
    return month


def next_month(d):
    days_in_month = calendar.monthrange(d.year, d.month)[1]
    last = d.replace(day=days_in_month)
    next_month = last + timedelta(days=1)
    month = 'month=' + str(next_month.year) + '-' + str(next_month.month)
    return month


# VIEWS
class GroupCreateView(CreateView):
    template_name = "create_group.html"
    form_class = CreateGroupForm
    success_url = "group:user_groups"

    # Overwrite django form initial for autofill create_by field
    def get_initial(self):
        self.initial.update({'created_by': self.request.user})
        return self.initial


@receiver(post_save, sender=Group)
def create_usergroup(sender, instance, created, **kwargs):
    if created:
        UserGroup.objects.create(group=instance, user_id=instance.created_by.id, is_admin=1, is_extra_user=1)


class UserGroupsView(ListView):
    model = UserGroup
    template_name = "groups_list.html"

    def get_queryset(self):
        queryset = super(UserGroupsView, self).get_queryset()
        queryset = queryset.filter(user_id=self.request.user.id)
        return queryset


# Need to add GroupMemberMixin
class GroupDetailView(View):
    html = "group_detail.html"
    context = {}

    def get(self, request, group_id):
        self.context['group'] = Group.objects.get(id=group_id)
        self.context['group_members'] = UserGroup.objects.filter(group_id=group_id).order_by('user__username')
        self.context['comments'] = Comment.objects.filter(group_id=group_id).order_by('-create_date')
        self.context['form_comment'] = GroupCommentForm
        # Code bellow is used in Jinja for visibility for allowed users
        if UserGroup.objects.filter(group_id=group_id, user_id=request.user.id, is_admin=True):
            self.context['is_admin'] = True
        else:
            self.context['is_admin'] = False
        if UserGroup.objects.filter(group_id=group_id, user_id=request.user.id, is_extra_user=True):
            self.context['is_extra'] = True
        else:
            self.context['is_extra'] = False

        # Calendar part below:
        # use today's date for the calendar
        d = get_date(self.request.GET.get('day', None))

        # Previous and next month pass to context
        d = get_date(self.request.GET.get('month', None))
        self.context['prev_month'] = prev_month(d)
        self.context['next_month'] = next_month(d)

        # Instantiate our calendar class with today's year and date
        cal = GroupCalendar(Group.objects.get(id=group_id), d.year, d.month)

        # Call the formatmonth method, which returns our calendar as a table
        html_cal = cal.formatmonth(withyear=True)
        self.context['calendar'] = mark_safe(html_cal)

        return render(request, self.html, self.context)

    def post(self, request, group_id):
        form_comment = GroupCommentForm(request.POST)
        if form_comment.is_valid():
            Comment.objects.create(content=form_comment.cleaned_data['content'], user=request.user, group_id=group_id)
        return redirect('group:group_details', group_id)


# Need to add GroupMemberMixin
class GroupAddEventView(View):

    context = {}

    def get(self, request, group_id):

        self.context['form'] = UserAddEventForm

        self.context['group'] = Group.objects.get(id=group_id)
        self.context['group_members'] = UserGroup.objects.filter(group_id=group_id).order_by('user__username')

        if UserGroup.objects.filter(group_id=group_id, user_id=request.user.id, is_admin=True):
            self.context['is_admin'] = True
        else:
            self.context['is_admin'] = False
        if UserGroup.objects.filter(group_id=group_id, user_id=request.user.id, is_extra_user=True):
            self.context['is_extra'] = True
        else:
            self.context['is_extra'] = False
        # html user_add_event nadaje się do tego dobrze, nie trzeba modyfikować kodu :)
        return render(request, 'group_add_event.html', self.context)

    def post(self, request, group_id):
        group = Group.objects.get(id=group_id)
        title = request.POST.get('name')
        description = request.POST.get('description')
        start_time = request.POST.get('start_time')
        # Atomic for unity event --> group events
        with transaction.atomic():
            new_event = Event.objects.create(name=title, description=description, start_time=start_time)
            # connecting event to the user
            group.group_events.add(Event.objects.get(id=new_event.id))
        return redirect('group:group_details', group_id=group_id)


# Need to add GroupMemberMixin
class GroupEventDetailsView(View):
    context = {}

    def get(self, request, group_id, event_id):
        self.context['group'] = Group.objects.get(id=group_id)
        self.context['group_members'] = UserGroup.objects.filter(group_id=group_id).order_by('user__username')
        # self.context['comments'] = Comment.objects.filter(group_id=None, event_id=event_id).order_by('create_date')
        self.context['event'] = Event.objects.get(id=event_id)
        # Tutaj nada się ten sam formularz co do dodawania komentarza w grupie
        # self.context['form_comment'] = GroupCommentForm
        if UserGroup.objects.filter(group_id=group_id, user_id=request.user.id, is_admin=True):
            self.context['is_admin'] = True
        else:
            self.context['is_admin'] = False
        if UserGroup.objects.filter(group_id=group_id, user_id=request.user.id, is_extra_user=True):
            self.context['is_extra'] = True
        else:
            self.context['is_extra'] = False
        return render(request, "group_event_details.html", self.context)

    def post(self, request, group_id, event_id):
        form_comment = GroupCommentForm(request.POST)
        if form_comment.is_valid():
            Comment.objects.create(content=form_comment.cleaned_data['content'], user=request.user, group_id=None,
                                   event_id=event_id, create_date=timezone.now)
        return redirect('group_event_details', group_id=group_id, event_id=event_id)


# Need to add GroupMemberMixin
class GroupEventDeleteView(View):

    def get(self, request, group_id, event_id):
        ctx = {'form': EventDeleteForm,
               'group': Group.objects.get(id=group_id),
               'event': Event.objects.get(id=event_id)}
        return render(request, "group_event_delete_confirm.html", ctx)

    def post(self, request, group_id, event_id):
        form = EventDeleteForm(request.POST)
        if form.is_valid():
            Event.objects.get(id=event_id).delete()
        return redirect("group:group_details", group_id=group_id)


# Need to add GroupMemberMixin
class AddMemberView(View):
    context = {}

    def get(self, request, group_id):
        self.context['group'] = Group.objects.get(id=group_id)
        self.context['group_members'] = UserGroup.objects.filter(group_id=group_id).order_by('user__username')
        # self.context['comments'] = Comment.objects.filter(group_id=group_id, event_id=None).order_by('create_date')

        # Whole mess bellow is because if statments in jinja did not work properly (for now is enough good):
        self.context['friends_to_invite'] = request.user.profile.friends.all()\
            .exclude(user__user_groups__group_id=group_id)
        if UserGroup.objects.filter(group_id=group_id, user_id=request.user.id, is_admin=True):
            self.context['is_admin'] = True
        else:
            self.context['is_admin'] = False
        if UserGroup.objects.filter(group_id=group_id, user_id=request.user.id, is_extra_user=True):
            self.context['is_extra'] = True
        else:
            self.context['is_extra'] = False
        return render(request, "add_user_to_group.html", self.context)

    def post(self, request, group_id):
        if 'add_normal' in request.POST:
            UserGroup.objects.create(group_id=group_id, user_id=request.POST['friend_id'],
                                     is_admin=False, is_extra_user=False)
            return redirect('group:add_member', group_id=group_id)

        elif 'add_extra' in request.POST:
            UserGroup.objects.create(group_id=group_id, user_id=request.POST['friend_id'],
                                     is_admin=False, is_extra_user=True)
            return redirect('group:add_member', group_id=group_id)


# Need to add GroupMemberMixin
class MemberUpdateView(View):
    context = {}
    html = "group_upgrade_member.html"

    def get(self, request, group_id, member_id):
        self.context['group'] = Group.objects.get(id=group_id)
        self.context['group_members'] = UserGroup.objects.filter(group_id=group_id).order_by('user__username')
        self.context['member'] = UserGroup.objects.get(user_id=member_id)
        if UserGroup.objects.filter(group_id=group_id, user_id=request.user.id, is_admin=True):
            self.context['is_admin'] = True
        else:
            self.context['is_admin'] = False
        if UserGroup.objects.filter(group_id=group_id, user_id=request.user.id, is_extra_user=True):
            self.context['is_extra'] = True
        else:
            self.context['is_extra'] = False
        return render(request, self.html, self.context)

    def post(self, request, group_id, member_id):
        member = UserGroup.objects.get(user_id=member_id)
        if request.POST.get('normal'):
            member.is_extra_user = False
            member.save()
        elif request.POST.get('extra'):
            member.is_extra_user = True
            member.save()
        elif request.POST.get('delete'):
            member.delete()
        return redirect('group:group_details', group_id=group_id)


# Need to add GroupMemberMixin
class DeleteComment(DeleteView):
    model = Comment

    def get_success_url(self):
        return reverse_lazy(
            'group:group_details', kwargs={'group_id': self.object.group_id}
        )