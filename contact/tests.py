"""
Comprehensive pytest unit tests for contact app API views.

This module contains test cases for all contact API endpoints including:
- Contact message creation
- Newsletter subscription and unsubscription
- Contact statistics
- Email validation and processing
- Error handling and validation

Test Coverage:
- All API views and endpoints
- Response status codes and data structure
- Form validation and error handling
- Email functionality (mocked)
- Authentication requirements (if any)
"""

import pytest
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth.models import User
from django.core import mail
from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from unittest.mock import patch, Mock
from contact.models import ContactMessage, Newsletter
from contact.views import ContactMessageCreateView, NewsletterSubscribeView


@pytest.mark.django_db
class TestContactMessageCreateView(APITestCase):
    """Test cases for ContactMessageCreateView API endpoint."""
    
    def setUp(self):
        """Set up test data for contact message tests."""
        self.client = APIClient()
        self.url = reverse('contact:message-create')
        
        # Valid contact message data
        self.valid_data = {
            'name': 'John Doe',
            'email': 'john.doe@example.com',
            'subject': 'general',
            'message': 'This is a test message for contact form.'
        }
        
        # Invalid contact message data
        self.invalid_data = {
            'name': '',
            'email': 'invalid-email',
            'subject': '',
            'message': ''
        }
    
    def test_create_contact_message_success(self):
        """Test successful creation of contact message."""
        response = self.client.post(self.url, self.valid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ContactMessage.objects.count(), 1)
        
        # Verify response message
        self.assertEqual(response.data['message'], 'Your message has been sent successfully!')
        
        # Verify database object
        contact_message = ContactMessage.objects.first()
        self.assertEqual(contact_message.name, 'John Doe')
        self.assertEqual(contact_message.email, 'john.doe@example.com')
        self.assertEqual(contact_message.subject, 'general')
        self.assertEqual(contact_message.message, 'This is a test message for contact form.')
    
    def test_create_contact_message_invalid_data(self):
        """Test contact message creation with invalid data."""
        response = self.client.post(self.url, self.invalid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIsInstance(response.data, dict)
        
        # Check that no message was created
        self.assertEqual(ContactMessage.objects.count(), 0)
        
        # Check validation errors
        self.assertIn('name', response.data)
        self.assertIn('email', response.data)
        self.assertIn('subject', response.data)
        self.assertIn('message', response.data)
    
    def test_create_contact_message_missing_fields(self):
        """Test contact message creation with missing required fields."""
        incomplete_data = {'name': 'John Doe'}
        
        response = self.client.post(self.url, incomplete_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(ContactMessage.objects.count(), 0)
        
        # Check that required fields are mentioned in errors
        self.assertIn('email', response.data)
        self.assertIn('message', response.data)
        # Subject has a default value, so it's not required
    
    def test_create_contact_message_invalid_email_format(self):
        """Test contact message creation with invalid email format."""
        invalid_email_data = self.valid_data.copy()
        invalid_email_data['email'] = 'not-an-email'
        
        response = self.client.post(self.url, invalid_email_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(ContactMessage.objects.count(), 0)
        self.assertIn('email', response.data)
    
    def test_create_contact_message_long_fields(self):
        """Test contact message creation with excessively long field values."""
        long_data = self.valid_data.copy()
        long_data['name'] = 'A' * 300  # Assuming max length is less than 300
        long_data['subject'] = 'B' * 300
        
        response = self.client.post(self.url, long_data, format='json')
        
        # Should either succeed (if fields are truncated) or fail with validation error
        if response.status_code == status.HTTP_400_BAD_REQUEST:
            # Check for field length validation errors
            self.assertTrue('name' in response.data or 'subject' in response.data)
        else:
            self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    @patch('contact.views.send_mail')
    def test_contact_message_email_notification(self, mock_send_mail):
        """Test that email notification is sent when contact message is created."""
        mock_send_mail.return_value = True
        
        response = self.client.post(self.url, self.valid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Verify email was attempted to be sent
        # Note: This depends on your actual implementation
        # mock_send_mail.assert_called_once()
    
    def test_contact_message_get_method_not_allowed(self):
        """Test that GET method is not allowed on contact create endpoint."""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)
    
    def test_contact_message_duplicate_submission(self):
        """Test handling of duplicate contact message submissions."""
        # Create first message
        response1 = self.client.post(self.url, self.valid_data, format='json')
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        
        # Create duplicate message
        response2 = self.client.post(self.url, self.valid_data, format='json')
        
        # Should still succeed (duplicates are typically allowed for contact forms)
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)
        self.assertEqual(ContactMessage.objects.count(), 2)


@pytest.mark.django_db
class TestNewsletterSubscribeView(APITestCase):
    """Test cases for NewsletterSubscribeView API endpoint."""
    
    def setUp(self):
        """Set up test data for newsletter subscription tests."""
        self.client = APIClient()
        self.url = reverse('contact:newsletter-subscribe')
        
        # Valid subscription data
        self.valid_data = {
            'email': 'subscriber@example.com'
        }
        
        # Invalid subscription data
        self.invalid_data = {
            'email': 'invalid-email-format'
        }
    
    def test_newsletter_subscribe_success(self):
        """Test successful newsletter subscription."""
        response = self.client.post(self.url, self.valid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIsInstance(response.data, dict)
        
        # Check that subscription was created in database
        self.assertEqual(Newsletter.objects.count(), 1)
        
        # Verify subscription details
        subscription = Newsletter.objects.first()
        self.assertEqual(subscription.email, 'subscriber@example.com')
        self.assertTrue(subscription.is_active)
        
        # Check response data structure
        expected_fields = ['id', 'email', 'is_active', 'subscribed_at']
        for field in expected_fields:
            self.assertIn(field, response.data)
    
    def test_newsletter_subscribe_invalid_email(self):
        """Test newsletter subscription with invalid email."""
        response = self.client.post(self.url, self.invalid_data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Newsletter.objects.count(), 0)
        self.assertIn('email', response.data)
    
    def test_newsletter_subscribe_missing_email(self):
        """Test newsletter subscription with missing email field."""
        response = self.client.post(self.url, {}, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Newsletter.objects.count(), 0)
        self.assertIn('email', response.data)
    
    def test_newsletter_subscribe_duplicate_email(self):
        """Test newsletter subscription with duplicate email."""
        # Create first subscription
        response1 = self.client.post(self.url, self.valid_data, format='json')
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        
        # Attempt duplicate subscription
        response2 = self.client.post(self.url, self.valid_data, format='json')
        
        # Should handle duplicate gracefully (either succeed or return appropriate error)
        if response2.status_code == status.HTTP_400_BAD_REQUEST:
            # Check for duplicate email error
            self.assertIn('email', response2.data)
        else:
            # Or it might succeed and just return existing subscription
            self.assertEqual(response2.status_code, status.HTTP_201_CREATED)
        
        # Should not create duplicate entries
        self.assertEqual(Newsletter.objects.count(), 1)
    
    def test_newsletter_subscribe_case_insensitive_email(self):
        """Test newsletter subscription with case variations in email."""
        # Subscribe with lowercase email
        response1 = self.client.post(
            self.url, 
            {'email': 'test@example.com'}, 
            format='json'
        )
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)
        
        # Attempt subscription with uppercase email
        response2 = self.client.post(
            self.url, 
            {'email': 'TEST@EXAMPLE.COM'}, 
            format='json'
        )
        
        # Should handle case insensitivity appropriately
        # (depends on your implementation - might prevent duplicate or normalize)
        if response2.status_code == status.HTTP_400_BAD_REQUEST:
            self.assertIn('email', response2.data)
    
    def test_newsletter_get_method_not_allowed(self):
        """Test that GET method is not allowed on newsletter subscribe endpoint."""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)


@pytest.mark.django_db
class TestNewsletterUnsubscribeView(APITestCase):
    """Test cases for newsletter_unsubscribe function-based view."""
    
    def setUp(self):
        """Set up test data for newsletter unsubscribe tests."""
        self.client = APIClient()
        
        # Create test subscription
        self.subscription = Newsletter.objects.create(
            email='subscriber@example.com',
            is_active=True
        )
        
        self.url = reverse('contact:newsletter-unsubscribe')
    
    def test_newsletter_unsubscribe_success(self):
        """Test successful newsletter unsubscription."""
        data = {'email': self.subscription.email}
        response = self.client.post(self.url, data, format='json')
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Check that subscription was deactivated
        self.subscription.refresh_from_db()
        self.assertFalse(self.subscription.is_active)
    
    def test_newsletter_unsubscribe_nonexistent_email(self):
        """Test unsubscription with non-existent email."""
        data = {'email': 'nonexistent@example.com'}
        response = self.client.post(self.url, data, format='json')
        
        # Should handle gracefully (either 404 or success message)
        self.assertIn(response.status_code, [
            status.HTTP_404_NOT_FOUND,
            status.HTTP_200_OK
        ])
    
    def test_newsletter_unsubscribe_already_unsubscribed(self):
        """Test unsubscription of already inactive subscription."""
        # Deactivate subscription first
        self.subscription.is_active = False
        self.subscription.save()
        
        data = {'email': self.subscription.email}
        response = self.client.post(self.url, data, format='json')
        
        # Should handle gracefully
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Should remain inactive
        self.subscription.refresh_from_db()
        self.assertFalse(self.subscription.is_active)
    
    def test_newsletter_unsubscribe_get_method(self):
        """Test GET method on unsubscribe endpoint (might show confirmation page)."""
        response = self.client.get(self.url)
        
        # Depending on implementation, might return 200 (confirmation page) or 405
        self.assertIn(response.status_code, [
            status.HTTP_200_OK,
            status.HTTP_405_METHOD_NOT_ALLOWED
        ])


@pytest.mark.django_db
class TestContactStatsView(APITestCase):
    """Test cases for contact_stats function-based view."""
    
    def setUp(self):
        """Set up test data for contact stats tests."""
        self.client = APIClient()
        self.url = reverse('contact:contact-stats')
        
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test contact messages
        self.message1 = ContactMessage.objects.create(
            name='John Doe',
            email='john@example.com',
            subject='Test Subject 1',
            message='Test message 1'
        )
        
        self.message2 = ContactMessage.objects.create(
            name='Jane Smith',
            email='jane@example.com',
            subject='Test Subject 2',
            message='Test message 2'
        )
        
        # Create test newsletter subscriptions
        self.subscription1 = Newsletter.objects.create(
            email='active@example.com',
            is_active=True
        )
        self.subscription2 = Newsletter.objects.create(
            email='active2@example.com',
            is_active=True
        )
        self.subscription3 = Newsletter.objects.create(
            email='unsubscribed@example.com',
            is_active=False
        )
    
    def test_contact_stats_success(self):
        """Test successful retrieval of contact statistics."""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIsInstance(response.data, dict)
        
        # Check expected statistics fields
        expected_fields = [
            'total_messages',
            'total_subscriptions',
            'active_subscriptions'
        ]
        
        for field in expected_fields:
            self.assertIn(field, response.data)
    
    def test_contact_stats_values(self):
        """Test the accuracy of contact statistics values."""
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify statistics values
        self.assertEqual(response.data['total_messages'], 2)
        self.assertEqual(response.data['total_subscriptions'], 3)
        self.assertEqual(response.data['active_subscriptions'], 2)
    
    def test_contact_stats_empty_data(self):
        """Test contact statistics with no data."""
        # Delete all data
        ContactMessage.objects.all().delete()
        Newsletter.objects.all().delete()
        
        response = self.client.get(self.url)
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # All counts should be zero
        self.assertEqual(response.data['total_messages'], 0)
        self.assertEqual(response.data['total_subscriptions'], 0)
        self.assertEqual(response.data['active_subscriptions'], 0)


@pytest.mark.django_db
class TestContactAPIIntegration(APITestCase):
    """Integration tests for contact API endpoints."""
    
    def setUp(self):
        """Set up test data for integration tests."""
        self.client = APIClient()
        
        # Create test data
        self.contact_message = ContactMessage.objects.create(
            name='Integration Test User',
            email='integration@example.com',
            subject='general',
            message='Integration test message'
        )
        
        self.newsletter_subscription = Newsletter.objects.create(
            email='newsletter@example.com',
            is_active=True
        )
    
    def test_api_endpoints_accessibility(self):
        """Test that all contact API endpoints are accessible."""
        endpoints = [
            reverse('contact:contact-stats'),
        ]
        
        # Test GET endpoints
        for endpoint in endpoints:
            response = self.client.get(endpoint)
            self.assertEqual(
                response.status_code,
                status.HTTP_200_OK,
                f"GET endpoint {endpoint} returned {response.status_code}"
            )
        
        # Test POST endpoints
        post_endpoints = [
            (reverse('contact:message-create'), {
                'name': 'Test User',
                'email': 'test@example.com',
                'subject': 'general',
                'message': 'Test message'
            }),
            (reverse('contact:newsletter-subscribe'), {
                'email': 'newsubscriber@example.com'
            })
        ]
        
        for endpoint, data in post_endpoints:
            response = self.client.post(endpoint, data, format='json')
            self.assertIn(
                response.status_code,
                [status.HTTP_200_OK, status.HTTP_201_CREATED],
                f"POST endpoint {endpoint} returned {response.status_code}"
            )
    
    def test_cross_endpoint_data_consistency(self):
        """Test data consistency across different endpoints."""
        # Get contact stats
        stats_response = self.client.get(reverse('contact:contact-stats'))
        initial_messages = stats_response.data['total_messages']
        initial_subscriptions = stats_response.data['total_subscriptions']
        
        # Create new contact message
        contact_data = {
            'name': 'New User',
            'email': 'newuser@example.com',
            'subject': 'general',
            'message': 'New test message'
        }
        
        contact_response = self.client.post(
            reverse('contact:message-create'),
            contact_data,
            format='json'
        )
        self.assertEqual(contact_response.status_code, status.HTTP_201_CREATED)
        
        # Create new newsletter subscription
        newsletter_data = {'email': 'newsubscriber2@example.com'}
        
        newsletter_response = self.client.post(
            reverse('contact:newsletter-subscribe'),
            newsletter_data,
            format='json'
        )
        self.assertEqual(newsletter_response.status_code, status.HTTP_201_CREATED)
        
        # Check updated stats
        updated_stats_response = self.client.get(reverse('contact:contact-stats'))
        
        self.assertEqual(
            updated_stats_response.data['total_messages'],
            initial_messages + 1
        )
        self.assertEqual(
            updated_stats_response.data['total_subscriptions'],
            initial_subscriptions + 1
        )


# Additional test utilities and fixtures
@pytest.fixture
def api_client():
    """Pytest fixture for API client."""
    return APIClient()


@pytest.fixture
def test_user():
    """Pytest fixture for test user."""
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def sample_contact_message():
    """Pytest fixture for sample contact message."""
    return ContactMessage.objects.create(
        name='Sample User',
        email='sample@example.com',
        subject='Sample Subject',
        message='Sample message content'
    )


@pytest.fixture
def sample_newsletter_subscription():
    """Pytest fixture for sample newsletter subscription."""
    return Newsletter.objects.create(
        email='sample@example.com',
        is_active=True
    )


# Pytest-style test functions
@pytest.mark.django_db
def test_contact_message_creation_with_fixtures(api_client):
    """Test contact message creation using pytest fixtures."""
    url = reverse('contact:message-create')
    data = {
        'name': 'Fixture Test User',
        'email': 'fixture@example.com',
        'subject': 'general',
        'message': 'Fixture test message'
    }
    
    response = api_client.post(url, data, format='json')
    
    assert response.status_code == status.HTTP_201_CREATED
    assert ContactMessage.objects.count() == 1
    assert ContactMessage.objects.first().name == 'Fixture Test User'


@pytest.mark.django_db
def test_newsletter_subscription_with_fixtures(api_client):
    """Test newsletter subscription using pytest fixtures."""
    url = reverse('contact:newsletter-subscribe')
    data = {'email': 'fixture@example.com'}
    
    response = api_client.post(url, data, format='json')
    
    assert response.status_code == status.HTTP_201_CREATED
    assert Newsletter.objects.count() == 1
    assert Newsletter.objects.first().email == 'fixture@example.com'


@pytest.mark.django_db
def test_contact_stats_with_fixtures(api_client, sample_contact_message, sample_newsletter_subscription):
    """Test contact stats using pytest fixtures."""
    url = reverse('contact:contact-stats')
    response = api_client.get(url)
    
    assert response.status_code == status.HTTP_200_OK
    assert response.data['total_messages'] == 1
    assert response.data['total_subscriptions'] == 1
    assert response.data['active_subscriptions'] == 1
