from unittest.mock import patch

from django.test import TestCase
import stripe


class StripeWebhookTests(TestCase):
    def test_webhook_returns_bad_request_for_stripe_errors(self):
        with patch(
            'budget.views.stripe.Webhook.construct_event',
            side_effect=stripe.StripeError('Unable to verify webhook')
        ):
            response = self.client.post(
                '/stripe/webhook/',
                data=b'{}',
                content_type='application/json',
                HTTP_STRIPE_SIGNATURE='test-signature',
            )

        self.assertEqual(response.status_code, 400)
