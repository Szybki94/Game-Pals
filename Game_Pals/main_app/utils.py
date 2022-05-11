from datetime import datetime, timedelta
from calendar import HTMLCalendar
from .models import Event


class StyleMixin:
    # formats a day as a td
    # filter events by day
    def formatday(self, day, events):
        events_per_day = events.filter(start_time__day=day).order_by('start_time')
        d = ""
        for event in events_per_day:
            d += f'''<li><a href="/event-details/{event.id}"> {event.name} </a></li>'''
        if day != 0:
            return f"<td><span class='date'>{day}</span><ul> {d} </ul></td>"
        return '<td></td>'

    # formats a week as a tr
    def formatweek(self, theweek, events):
        week = ''
        for d, weekday in theweek:
            week += self.formatday(d, events)
        return f'<tr> {week} </tr>'

    # formats a month as a table
    # filter events by year and month
    def formatmonth(self, withyear=True):
        events = self.get_events()

        cal = f'<table border="0" cellpadding="0" cellspacing="0" class="calendar">\n'
        cal += f'{self.formatmonthname(self.year, self.month, withyear=withyear)}\n'
        cal += f'{self.formatweekheader()}\n'
        for week in self.monthdays2calendar(self.year, self.month):
            cal += f'{self.formatweek(week, events)}\n'
        return cal

    def get_events(self):
        raise NotImplemented


class Calendar(StyleMixin, HTMLCalendar):
    def __init__(self, user, year=None, month=None, ):
        self.year = year
        self.month = month
        self.user = user
        super().__init__()

    def get_events(self):
        events = Event.objects.filter(user=self.user, start_time__year=self.year, start_time__month=self.month)
        return events


class GroupCalendar(StyleMixin, HTMLCalendar):
    def __init__(self, group_id, year=None, month=None, ):
        self.year = year
        self.month = month
        self.group = group_id
        super().__init__()

    # formats a day as a td
    # filter events by day
    # Nadpisałem te funkcję jescze raz, ponieważ musiałem zmienić przekierowanie
    def formatday(self, day, events):
        events_per_day = events.filter(start_time__day=day).order_by('start_time')
        d = ""
        for event in events_per_day:
            d += f'''<li><a href="/group-details/{event.group.id}/event-details/{event.id}"> {event.name} </a></li>'''
        if day != 0:
            return f"<td><span class='date'>{day}</span><ul> {d} </ul></td>"
        return '<td></td>'

    def get_events(self):
        events = Event.objects.filter(group=self.group, start_time__year=self.year, start_time__month=self.month)
        return events
