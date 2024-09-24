from django.test import TestCase
from django.core import mail
from django.conf import settings
from accounts.utils import send_notification

class SendNotificationTest(TestCase):
    
    def test_send_notification_single_email(self):
        context = {
            'to_email': 'test@example.com',  # A single email address
        }
        send_notification(
            mail_subject="Test Email",
            mail_template='orders/order_confirmation_email.html',  # Use an actual email template path
            context=context
        )

        # Verify an email has been sent
        self.assertEqual(len(mail.outbox), 1)  # One email should be sent
        self.assertEqual(mail.outbox[0].subject, 'Test Email')
        self.assertIn('test@example.com', mail.outbox[0].to)
    
    def test_send_notification_multiple_emails(self):
        context = {
            'to_email': ['test1@example.com', 'test2@example.com'],  # A list of emails
        }
        send_notification(
            mail_subject="Test Multiple Emails",
            mail_template='orders/order_confirmation_email.html',
            context=context
        )

        # Verify an email has been sent
        self.assertEqual(len(mail.outbox), 1)  # One email should be sent
        self.assertEqual(mail.outbox[0].subject, 'Test Multiple Emails')
        self.assertIn('test1@example.com', mail.outbox[0].to)
        self.assertIn('test2@example.com', mail.outbox[0].to)
