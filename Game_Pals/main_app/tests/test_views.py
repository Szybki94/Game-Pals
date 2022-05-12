import pytest

from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from ..models import Profile, Event, Group, Invitation, UserGroup, Game, UserGames, \
    Comment


class TestViews(TestCase):

    def setUp(self):
        self.client = Client()
        self.login_url = reverse('login')

    def test_can_access_login(self):
        response = self.client.get(self.login_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'login_page.html')


