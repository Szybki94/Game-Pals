from django.test import SimpleTestCase
from django.urls import reverse, resolve
from ..views import MainView, HomeView, LoginView, LogoutView, RegisterView, \
    UserUpdateView1, UserUpdateView2, UserAddEventView, UserAddGamesView, UserDeleteGameView, \
    UserSearchView, EventDetailsView


class TestUrls(SimpleTestCase):

    def test_url_main_is_resolved(self):
        url = reverse('main')
        print(resolve(url))
        self.assertEquals(resolve(url).func.view_class, MainView)

    def test_url_home_is_resolved(self):
        url = reverse('home')
        print(resolve(url))
        self.assertEquals(resolve(url).func.view_class, HomeView)

    def test_url_login_is_resolved(self):
        url = reverse('login')
        print(resolve(url))
        self.assertEquals(resolve(url).func.view_class, LoginView)

    def test_url_logout_is_resolved(self):
        url = reverse('logout')
        print(resolve(url))
        self.assertEquals(resolve(url).func.view_class, LogoutView)

    def test_url_register_is_resolved(self):
        url = reverse('register')
        print(resolve(url))
        self.assertEquals(resolve(url).func.view_class, RegisterView)

    def test_url_update1_is_resolved(self):
        url = reverse('user-update-1')
        print(resolve(url))
        self.assertEquals(resolve(url).func.view_class, UserUpdateView1)

    def test_url_update2_is_resolved(self):
        url = reverse('user-update-2')
        print(resolve(url))
        self.assertEquals(resolve(url).func.view_class, UserUpdateView2)

    def test_url_add_event_is_resolved(self):
        url = reverse('user_add_event')
        print(resolve(url))
        self.assertEquals(resolve(url).func.view_class, UserAddEventView)

    def test_url_add_games_is_resolved(self):
        url = reverse('user_add_games')
        print(resolve(url))
        self.assertEquals(resolve(url).func.view_class, UserAddGamesView)

    def test_url_delete_games_is_resolved(self):
        url = reverse('user_delete_games', kwargs={'game_id': 1})
        print(resolve(url))
        self.assertEquals(resolve(url).func.view_class, UserDeleteGameView)

    def test_url_user_search_is_resolved(self):
        url = reverse('user_search')
        print(resolve(url))
        self.assertEquals(resolve(url).func.view_class, UserSearchView)

    def test_url_event_details_is_resolved(self):
        url = reverse('event_details', kwargs={'event_id': 1})
        print(resolve(url))
        self.assertEquals(resolve(url).func.view_class, EventDetailsView)
