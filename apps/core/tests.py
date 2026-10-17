from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse


class HomeViewTests(TestCase):
    def test_home_renders_for_authenticated_user(self):
        user = get_user_model().objects.create_user(username='admin', is_superuser=True, password='secret1234')

        self.client.force_login(user)
        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'home.html')

    def test_home_requires_login(self):
        response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.status_code, 302)


class RoleRedirectTests(TestCase):
    def test_regular_user_redirected_from_dashboard_to_chat(self):
        user = get_user_model().objects.create_user(
            username='user1', email='user1@example.com', password='user-pass-123')
        self.client.force_login(user)
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('chat:page'))

    def test_superuser_keeps_dashboard(self):
        su = get_user_model().objects.create_user(
            username='root', email='root@example.com', password='root-pass-123', is_superuser=True)
        self.client.force_login(su)
        response = self.client.get(reverse('dashboard'))
        self.assertEqual(response.status_code, 200)

    def test_login_post_sends_regular_user_to_chat(self):
        get_user_model().objects.create_user(
            username='user2', email='user2@example.com', password='user-pass-123')
        response = self.client.post(reverse('login'), {
            'email': 'user2@example.com', 'password': 'user-pass-123'})
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('chat:page'))
