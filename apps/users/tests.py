from unittest import mock

from django.test import TestCase
from django.urls import reverse

from apps.users.models import User


class UserDeactivationTests(TestCase):
    def setUp(self):
        self.admin = User.objects.create_user(
            username='admin2', email='admin2@example.com', password='admin-pass-123',
            is_superuser=True, is_staff=True,
        )
        self.user = User.objects.create_user(
            username='juan', email='juan@example.com', password='juan-pass-123',
        )
        self.client.force_login(self.admin)

    def test_admin_hidden_from_users_list(self):
        res = self.client.get(reverse('users:user_list'))
        self.assertEqual(res.status_code, 200)
        listed_ids = [u.pk for u in res.context['users']]
        self.assertNotIn(self.admin.pk, listed_ids)
        self.assertIn(self.user.pk, listed_ids)

    def test_temporary_deactivate(self):
        res = self.client.post(
            reverse('users:user_deactivate_ajax', args=[self.user.pk]), {'mode': 'temporary'},
        )
        self.assertEqual(res.status_code, 200)
        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)
        self.assertFalse(self.user.is_permanently_deactivated)

    def test_forever_deactivate_deletes_account(self):
        user_pk = self.user.pk
        res = self.client.post(
            reverse('users:user_deactivate_ajax', args=[user_pk]), {'mode': 'forever'},
        )
        self.assertEqual(res.status_code, 200)
        self.assertFalse(User.objects.filter(pk=user_pk).exists())

    def test_reactivate_temporary(self):
        self.client.post(
            reverse('users:user_deactivate_ajax', args=[self.user.pk]), {'mode': 'temporary'},
        )
        res = self.client.post(reverse('users:user_reactivate_ajax', args=[self.user.pk]))
        self.assertEqual(res.status_code, 200)
        self.user.refresh_from_db()
        self.assertTrue(self.user.is_active)

    def test_cannot_deactivate_superuser(self):
        res = self.client.post(
            reverse('users:user_deactivate_ajax', args=[self.admin.pk]), {'mode': 'forever'},
        )
        self.assertEqual(res.status_code, 404)
        self.admin.refresh_from_db()
        self.assertTrue(self.admin.is_active)
        self.assertFalse(self.admin.is_permanently_deactivated)

    def test_legacy_permanent_flag_blocks_reactivation(self):
        self.user.is_permanently_deactivated = True
        self.user.is_active = False
        self.user.save(update_fields=['is_permanently_deactivated', 'is_active'])
        res = self.client.post(reverse('users:user_reactivate_ajax', args=[self.user.pk]))
        self.assertEqual(res.status_code, 400)

    def test_sort_by_usage_puts_top_spender_first(self):
        other = User.objects.create_user(
            username='pedro', email='pedro@example.com', password='pedro-pass-123',
        )
        usage = {
            str(self.user.pk): {'username': 'juan', 'total_tokens': 500,
                                'engines': {'groq': {'total_tokens': 500}}},
            str(other.pk): {'username': 'pedro', 'total_tokens': 5,
                            'engines': {'groq': {'total_tokens': 5}}},
        }
        with mock.patch('apps.chat.services.ai.get_usage_by_user', return_value=usage):
            res = self.client.get(reverse('users:user_list'), {'sort': 'usage'})
        self.assertEqual(res.status_code, 200)
        listed = [u.pk for u in res.context['users']]
        self.assertEqual(listed[0], self.user.pk)
