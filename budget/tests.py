from types import SimpleNamespace
from unittest.mock import patch

from django.contrib.auth.models import User
from django.http import Http404, HttpResponse
from django.test import RequestFactory, TestCase
from django.urls import reverse

import stripe

from budget.models import Category, Profile, Transaction
from budget.views import edit_transaction


class StripeWebhookTests(TestCase):
    def test_webhook_returns_bad_request_for_stripe_errors(self):
        with patch(
            'budget.views.stripe.Webhook.construct_event',
            side_effect=stripe.error.SignatureVerificationError(
                'Unable to verify webhook',
                'test-signature'
            )
        ):
            response = self.client.post(
                '/stripe/webhook/',
                data=b'{}',
                content_type='application/json',
                HTTP_STRIPE_SIGNATURE='test-signature',
            )

        self.assertEqual(response.status_code, 400)

    def test_webhook_returns_ok_on_unexpected_processing_error(self):
        event = {
            'type': 'checkout.session.completed',
            'data': {
                'object': {
                    'payment_status': 'paid',
                    'client_reference_id': '1',
                }
            },
        }

        with patch(
            'budget.views.stripe.Webhook.construct_event',
            return_value=event,
        ), patch(
            'budget.views.Profile.objects.get_or_create',
            side_effect=Exception('db failure'),
        ):
            response = self.client.post(
                '/stripe/webhook/',
                data=b'{}',
                content_type='application/json',
                HTTP_STRIPE_SIGNATURE='test-signature',
            )

        self.assertEqual(response.status_code, 200)

    def test_checkout_success_activates_premium_when_session_is_paid(self):
        user = User.objects.create_user(
            username='testuser',
            password='testpass123',
        )
        self.client.force_login(user)
        Profile.objects.get_or_create(user=user)

        with patch(
            'budget.views.stripe.checkout.Session.retrieve',
            return_value=SimpleNamespace(
                payment_status='paid',
                client_reference_id=str(user.id),
            ),
        ), patch(
            'budget.views.render',
            return_value=HttpResponse('ok'),
        ):
            response = self.client.get('/checkout-success/?session_id=test-session-id')

        self.assertEqual(response.status_code, 200)
        self.assertTrue(Profile.objects.get(user=user).is_premium)


class AuthAndOwnershipTests(TestCase):
    def assert_logged_in_user_redirects(self, username, start_url):
        user = User.objects.create_user(
            username=username,
            password='testpass123',
        )

        self.client.force_login(user)

        response = self.client.get(start_url)

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('dashboard'))

    def test_user_can_signup(self):
        response = self.client.post(
            reverse('signup'),
            data={
                'username': 'newuser',
                'password1': 'StrongPass123!',
                'password2': 'StrongPass123!',
            },
            follow=False,
        )

        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, reverse('login'))
        self.assertTrue(User.objects.filter(username='newuser').exists())

    def test_logged_in_user_redirected_from_signup(self):
        self.assert_logged_in_user_redirects('existinguser', reverse('signup'))

    def test_logged_in_user_redirected_from_login(self):
        self.assert_logged_in_user_redirects('existinguser2', reverse('login'))

    def test_anonymous_users_are_redirected_from_protected_pages(self):
        protected_urls = [
            reverse('dashboard'),
            reverse('transactions'),
        ]

        for url in protected_urls:
            response = self.client.get(url)
            self.assertEqual(response.status_code, 302)
            self.assertIn('/accounts/login/', response.url)

    def test_user_cannot_edit_another_users_transaction(self):
        factory = RequestFactory()
        owner = User.objects.create_user(
            username='owner',
            password='testpass123',
        )
        other_user = User.objects.create_user(
            username='other',
            password='testpass123',
        )

        category = Category.objects.create(
            name='Salary',
            type='income',
            user=owner,
        )
        transaction = Transaction.objects.create(
            user=owner,
            category=category,
            amount='100.00',
            date='2026-07-09',
            description='Paycheck',
        )

        request = factory.get(reverse('edit_transaction', args=[transaction.id]))
        request.user = other_user

        with self.assertRaises(Http404):
            edit_transaction(request, transaction.id)

    def test_premium_cannot_activate_without_successful_payment(self):
        user = User.objects.create_user(
            username='premiumuser',
            password='testpass123',
        )
        self.client.force_login(user)

        with patch(
            'budget.views.stripe.checkout.Session.retrieve',
            return_value=SimpleNamespace(
                payment_status='unpaid',
                client_reference_id=str(user.id),
            ),
        ), patch(
            'budget.views.render',
            return_value=HttpResponse('ok'),
        ):
            response = self.client.get('/checkout-success/?session_id=test-session-id')

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Profile.objects.get(user=user).is_premium)
