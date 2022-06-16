import pytest

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from ..models import Group, UserGroup
User = get_user_model()


class UserTest(TestCase):

    def setUp(self):
        # set up for user_a
        user_a_pw = 'alamakota1'
        self.user_a_pw = user_a_pw
        user_a = User(username='Test_1', email='test_1@gmail.com', )
        user_a.is_staff = True
        user_a.is_superuser = True
        user_a.set_password(user_a_pw)
        user_a.save()
        self.user_a = user_a

    # Testy napisane na rozgrzewkę
    def test_user_exists(self):
        user_count = User.objects.all().count()
        self.assertEqual(user_count, 1)
        self.assertNotEqual(user_count, 0)

    def test_user_password_correct(self):
        self.assertTrue(self.user_a.check_password(self.user_a_pw))

    def test_user_password_wrong(self):
        self.assertFalse(self.user_a.check_password('alamapsa1'))

    # test sprawdzający login view
    def test_login_correct(self):
        login_url = reverse('login')
        data = {
            'username': self.user_a.username,
            'password': self.user_a_pw
        }
        response = self.client.post(login_url, data, follow=True)
        # print(dir(response))
        status_code = response.status_code
        redirect_path = response.request.get('PATH_INFO')
        # sprawdzam, czy zostanę dobrze przekierowany
        self.assertEqual(redirect_path, reverse('home'))
        # sprawdzam, czy dostałem się w dobre miejsce
        self.assertEqual(status_code, 200)


class GroupTest(TestCase):

    def setUp(self):
        # set up for user_a -> member of group
        user_a_pw = 'alamakota1'
        self.user_a_pw = user_a_pw
        user_a = User(username='Test_1', email='test_1@gmail.com', )
        user_a.is_staff = True
        user_a.is_superuser = True
        user_a.set_password(user_a_pw)
        user_a.save()
        self.user_a = user_a

        # client_a będzie to user_a z uprawnieniami
        client_a = Client()
        client_a.login(username=user_a, password=user_a_pw)
        self.client_a = client_a

        # set up for user_b -> NOT member of group
        user_b_pw = 'alamakota1'
        self.user_b_pw = user_b_pw
        user_b = User(username='Test_2', email='test_2@gmail.com', )
        user_b.is_staff = False
        user_b.is_superuser = False
        user_b.set_password(user_b_pw)
        user_b.save()
        self.user_b = user_b

        # client_a będzie to user_a z uprawnieniami
        client_b = Client()
        client_b.login(username=user_b, password=user_b_pw)
        self.client_b = client_b

        # set up for group
        group_a = Group.objects.create(name='Test_group', created_by_id=user_a.id, is_active=True)
        group_a.save()
        self.group_a = group_a

        # set up for UserGroup (in this case receiver should create UserGroup object, so I update only row)
        user_group_a = UserGroup.objects.filter(group=group_a).first()
        user_group_a.user = user_a
        user_group_a.group = group_a
        user_group_a.is_admin = True
        user_group_a.is_extra = False
        user_group_a.save()
        self.user_group_a = user_group_a

    def test_objects_create(self):
        user_count = User.objects.all().count()
        group_count = Group.objects.all().count()
        user_group_count = UserGroup.objects.all().count()
        self.assertEqual(user_count, 2)
        self.assertEqual(group_count, 1)
        self.assertEqual(user_group_count, 1)

    def test_access_group(self):
        group_url = reverse('group-details', kwargs={'group_id': self.group_a.id})
        # test for member
        response_a = self.client_a.get(group_url)
        self.assertEqual(response_a.status_code, 200)
        # test for NOT member
        response_b = self.client_b.get(group_url)
        self.assertNotEqual(response_b.status_code, 200)
