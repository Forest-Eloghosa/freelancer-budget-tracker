from unittest.mock import patch
from types import SimpleNamespace

from django.contrib.auth.models import User
from django.http import HttpResponse
from django.test import TestCase
import stripe
from budget.models import Profile


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
