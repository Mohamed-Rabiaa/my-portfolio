"""
Comprehensive pytest tests for contact application serializers.

This module provides thorough testing for all contact DRF serializers including:
- ContactMessageSerializer: contact form submission serialization and validation
- NewsletterSerializer: newsletter subscription serialization and validation

Tests cover:
- Serialization of model instances to JSON
- Deserialization and validation of input data
- Field validation and constraints
- Choice field validation (subject categories, status workflow)
- Email field validation and uniqueness
- Custom validation methods
- Error handling and validation messages
"""

import pytest
from django.test import TestCase
from rest_framework import serializers
from contact.models import ContactMessage, Newsletter
from contact.serializers import ContactMessageSerializer, NewsletterSerializer
from datetime import datetime


@pytest.mark.django_db
class TestContactMessageSerializer:
    """Test cases for the ContactMessageSerializer."""
    
    @pytest.fixture
    def contact_message_data(self):
        """Sample contact message data for testing."""
        return {
            'name': 'John Doe',
            'email': 'john@example.com',
            'subject': 'project',
            'message': 'I would like to discuss a potential project collaboration.',
            'ip_address': '192.168.1.1',
            'user_agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
    
    def test_contact_message_serialization(self):
        """Test serializing a contact message instance."""
        message = ContactMessage.objects.create(
            name='Jane Smith',
            email='jane@example.com',
            subject='job',
            message='I am interested in job opportunities.',
            status='new',
            ip_address='203.0.113.1',
            user_agent='Mozilla/5.0 Test Browser'
        )
        
        serializer = ContactMessageSerializer(message)
        data = serializer.data
        
        assert data['id'] == message.id
        assert data['name'] == 'Jane Smith'
        assert data['email'] == 'jane@example.com'
        assert data['subject'] == 'job'
        assert data['message'] == 'I am interested in job opportunities.'
        assert data['status'] == 'new'
        assert data['get_subject_display'] == 'Job Opportunity'
        assert data['get_status_display'] == 'New'
        assert data['is_new'] is True
        assert data['ip_address'] == '203.0.113.1'
        assert data['user_agent'] == 'Mozilla/5.0 Test Browser'
        assert 'created_at' in data
        assert 'updated_at' in data
    
    def test_contact_message_deserialization_valid(self, contact_message_data):
        """Test deserializing valid contact message data."""
        serializer = ContactMessageSerializer(data=contact_message_data)
        
        assert serializer.is_valid(), serializer.errors
        message = serializer.save()
        
        assert message.name == 'John Doe'
        assert message.email == 'john@example.com'
        assert message.subject == 'project'
        assert message.message == 'I would like to discuss a potential project collaboration.'
        assert message.status == 'new'  # Default status
        assert message.ip_address == '192.168.1.1'
        assert message.user_agent == 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
    
    def test_contact_message_deserialization_minimal_data(self):
        """Test deserializing contact message with minimal required data."""
        minimal_data = {
            'name': 'Minimal User',
            'email': 'minimal@example.com',
            'message': 'Minimal message content.'
        }
        
        serializer = ContactMessageSerializer(data=minimal_data)
        assert serializer.is_valid(), serializer.errors
        
        message = serializer.save()
        assert message.name == 'Minimal User'
        assert message.email == 'minimal@example.com'
        assert message.message == 'Minimal message content.'
        assert message.subject == 'general'  # Default subject
        assert message.status == 'new'  # Default status
        assert message.ip_address == ''  # Optional field
        assert message.user_agent == ''  # Optional field
    
    def test_contact_message_deserialization_invalid_name(self, contact_message_data):
        """Test deserializing contact message with invalid name."""
        contact_message_data['name'] = ''  # Empty name
        
        serializer = ContactMessageSerializer(data=contact_message_data)
        assert not serializer.is_valid()
        assert 'name' in serializer.errors
    
    def test_contact_message_deserialization_invalid_email(self, contact_message_data):
        """Test deserializing contact message with invalid email."""
        invalid_emails = [
            '',  # Empty email
            'invalid-email',  # Invalid format
            'user@',  # Incomplete email
            '@domain.com',  # Missing user part
            'user space@domain.com'  # Space in email
        ]
        
        for invalid_email in invalid_emails:
            contact_message_data['email'] = invalid_email
            serializer = ContactMessageSerializer(data=contact_message_data)
            assert not serializer.is_valid(), f"Email '{invalid_email}' should be invalid"
            assert 'email' in serializer.errors
    
    def test_contact_message_deserialization_invalid_message(self, contact_message_data):
        """Test deserializing contact message with invalid message."""
        contact_message_data['message'] = ''  # Empty message
        
        serializer = ContactMessageSerializer(data=contact_message_data)
        assert not serializer.is_valid()
        assert 'message' in serializer.errors
    
    def test_contact_message_subject_choices_validation(self, contact_message_data):
        """Test contact message subject choices validation."""
        # Valid subjects
        valid_subjects = ['general', 'project', 'job', 'freelance', 'other']
        
        for subject in valid_subjects:
            contact_message_data['subject'] = subject
            serializer = ContactMessageSerializer(data=contact_message_data)
            assert serializer.is_valid(), f"Subject '{subject}' should be valid"
        
        # Invalid subject
        contact_message_data['subject'] = 'invalid_subject'
        serializer = ContactMessageSerializer(data=contact_message_data)
        assert not serializer.is_valid()
        assert 'subject' in serializer.errors
    
    def test_contact_message_status_choices_validation(self, contact_message_data):
        """Test contact message status choices validation."""
        # Valid statuses
        valid_statuses = ['new', 'read', 'replied', 'archived']
        
        for status in valid_statuses:
            contact_message_data['status'] = status
            serializer = ContactMessageSerializer(data=contact_message_data)
            assert serializer.is_valid(), f"Status '{status}' should be valid"
        
        # Invalid status
        contact_message_data['status'] = 'invalid_status'
        serializer = ContactMessageSerializer(data=contact_message_data)
        assert not serializer.is_valid()
        assert 'status' in serializer.errors
    
    def test_contact_message_display_methods(self):
        """Test that display methods are included in serialized data."""
        message = ContactMessage.objects.create(
            name='Display Test',
            email='display@example.com',
            subject='freelance',
            message='Testing display methods',
            status='replied'
        )
        
        serializer = ContactMessageSerializer(message)
        data = serializer.data
        
        assert data['get_subject_display'] == 'Freelance Work'
        assert data['get_status_display'] == 'Replied'
        assert data['is_new'] is False  # Status is 'replied', not 'new'
    
    def test_contact_message_is_new_property(self):
        """Test is_new property in serialized data."""
        # New message
        new_message = ContactMessage.objects.create(
            name='New User',
            email='new@example.com',
            message='New message',
            status='new'
        )
        
        serializer = ContactMessageSerializer(new_message)
        data = serializer.data
        assert data['is_new'] is True
        
        # Read message
        read_message = ContactMessage.objects.create(
            name='Read User',
            email='read@example.com',
            message='Read message',
            status='read'
        )
        
        serializer = ContactMessageSerializer(read_message)
        data = serializer.data
        assert data['is_new'] is False
    
    def test_contact_message_update(self):
        """Test updating a contact message through serializer."""
        message = ContactMessage.objects.create(
            name='Original Name',
            email='original@example.com',
            subject='general',
            message='Original message',
            status='new'
        )
        
        update_data = {
            'status': 'read'
        }
        
        serializer = ContactMessageSerializer(message, data=update_data, partial=True)
        assert serializer.is_valid()
        
        updated_message = serializer.save()
        assert updated_message.status == 'read'
        assert updated_message.name == 'Original Name'  # Unchanged
        assert updated_message.email == 'original@example.com'  # Unchanged
    
    def test_contact_message_long_content_validation(self, contact_message_data):
        """Test handling of long content in message field."""
        # Very long message (should be accepted)
        long_message = 'A' * 2000
        contact_message_data['message'] = long_message
        
        serializer = ContactMessageSerializer(data=contact_message_data)
        assert serializer.is_valid(), serializer.errors
        
        message = serializer.save()
        assert len(message.message) == 2000
    
    def test_contact_message_ip_address_validation(self, contact_message_data):
        """Test IP address field validation."""
        # Valid IP addresses
        valid_ips = [
            '192.168.1.1',
            '10.0.0.1',
            '127.0.0.1',
            '203.0.113.1',
            '2001:0db8:85a3:0000:0000:8a2e:0370:7334',  # IPv6
            ''  # Empty is allowed
        ]
        
        for ip in valid_ips:
            contact_message_data['ip_address'] = ip
            serializer = ContactMessageSerializer(data=contact_message_data)
            assert serializer.is_valid(), f"IP address '{ip}' should be valid"


@pytest.mark.django_db
class TestNewsletterSerializer:
    """Test cases for the NewsletterSerializer."""
    
    @pytest.fixture
    def newsletter_data(self):
        """Sample newsletter data for testing."""
        return {
            'email': 'subscriber@example.com',
            'name': 'Newsletter Subscriber',
            'ip_address': '192.168.1.100'
        }
    
    def test_newsletter_serialization(self):
        """Test serializing a newsletter subscription instance."""
        subscription = Newsletter.objects.create(
            email='test@example.com',
            name='Test Subscriber',
            is_active=True,
            ip_address='203.0.113.100'
        )
        
        serializer = NewsletterSerializer(subscription)
        data = serializer.data
        
        assert data['id'] == subscription.id
        assert data['email'] == 'test@example.com'
        assert data['name'] == 'Test Subscriber'
        assert data['is_active'] is True
        assert data['ip_address'] == '203.0.113.100'
        assert 'subscribed_at' in data
    
    def test_newsletter_deserialization_valid(self, newsletter_data):
        """Test deserializing valid newsletter data."""
        serializer = NewsletterSerializer(data=newsletter_data)
        
        assert serializer.is_valid(), serializer.errors
        subscription = serializer.save()
        
        assert subscription.email == 'subscriber@example.com'
        assert subscription.name == 'Newsletter Subscriber'
        assert subscription.is_active is True  # Default value
        assert subscription.ip_address == '192.168.1.100'
    
    def test_newsletter_deserialization_minimal_data(self):
        """Test deserializing newsletter with minimal required data."""
        minimal_data = {
            'email': 'minimal@example.com'
        }
        
        serializer = NewsletterSerializer(data=minimal_data)
        assert serializer.is_valid(), serializer.errors
        
        subscription = serializer.save()
        assert subscription.email == 'minimal@example.com'
        assert subscription.name == ''  # Optional field
        assert subscription.is_active is True  # Default value
        assert subscription.ip_address == ''  # Optional field
    
    def test_newsletter_deserialization_invalid_email(self, newsletter_data):
        """Test deserializing newsletter with invalid email."""
        invalid_emails = [
            '',  # Empty email
            'invalid-email',  # Invalid format
            'user@',  # Incomplete email
            '@domain.com',  # Missing user part
            'user space@domain.com'  # Space in email
        ]
        
        for invalid_email in invalid_emails:
            newsletter_data['email'] = invalid_email
            serializer = NewsletterSerializer(data=newsletter_data)
            assert not serializer.is_valid(), f"Email '{invalid_email}' should be invalid"
            assert 'email' in serializer.errors
    
    def test_newsletter_unique_email_validation(self):
        """Test that newsletter emails must be unique."""
        # Create existing subscription
        Newsletter.objects.create(
            email='existing@example.com',
            name='Existing Subscriber'
        )
        
        # Try to create another subscription with same email
        duplicate_data = {
            'email': 'existing@example.com',
            'name': 'Duplicate Subscriber'
        }
        
        serializer = NewsletterSerializer(data=duplicate_data)
        assert not serializer.is_valid()
        assert 'email' in serializer.errors
    
    def test_newsletter_email_validation_formats(self, newsletter_data):
        """Test various valid email formats."""
        valid_emails = [
            'user@domain.com',
            'user.name@domain.co.uk',
            'user+tag@domain.org',
            '123@domain.net',
            'user-name@sub.domain.com'
        ]
        
        for email in valid_emails:
            newsletter_data['email'] = email
            serializer = NewsletterSerializer(data=newsletter_data)
            assert serializer.is_valid(), f"Email '{email}' should be valid"
    
    def test_newsletter_is_active_default(self, newsletter_data):
        """Test that newsletter subscriptions are active by default."""
        # Don't specify is_active in data
        del newsletter_data['name']  # Make it minimal
        del newsletter_data['ip_address']
        
        serializer = NewsletterSerializer(data=newsletter_data)
        assert serializer.is_valid()
        
        subscription = serializer.save()
        assert subscription.is_active is True
    
    def test_newsletter_is_active_explicit_false(self, newsletter_data):
        """Test newsletter subscription with is_active explicitly set to False."""
        newsletter_data['is_active'] = False
        
        serializer = NewsletterSerializer(data=newsletter_data)
        assert serializer.is_valid()
        
        subscription = serializer.save()
        assert subscription.is_active is False
    
    def test_newsletter_optional_fields(self, newsletter_data):
        """Test newsletter with optional fields."""
        # Test with name but no IP address
        newsletter_data['ip_address'] = ''
        
        serializer = NewsletterSerializer(data=newsletter_data)
        assert serializer.is_valid()
        
        subscription = serializer.save()
        assert subscription.name == 'Newsletter Subscriber'
        assert subscription.ip_address == ''
        
        # Test with IP address but no name
        newsletter_data2 = {
            'email': 'noname@example.com',
            'name': '',
            'ip_address': '10.0.0.1'
        }
        
        serializer2 = NewsletterSerializer(data=newsletter_data2)
        assert serializer2.is_valid()
        
        subscription2 = serializer2.save()
        assert subscription2.name == ''
        assert subscription2.ip_address == '10.0.0.1'
    
    def test_newsletter_update(self):
        """Test updating a newsletter subscription through serializer."""
        subscription = Newsletter.objects.create(
            email='update@example.com',
            name='Original Name',
            is_active=True
        )
        
        update_data = {
            'name': 'Updated Name',
            'is_active': False
        }
        
        serializer = NewsletterSerializer(subscription, data=update_data, partial=True)
        assert serializer.is_valid()
        
        updated_subscription = serializer.save()
        assert updated_subscription.name == 'Updated Name'
        assert updated_subscription.is_active is False
        assert updated_subscription.email == 'update@example.com'  # Unchanged
    
    def test_newsletter_ip_address_validation(self, newsletter_data):
        """Test IP address field validation for newsletter."""
        # Valid IP addresses
        valid_ips = [
            '192.168.1.1',
            '10.0.0.1',
            '127.0.0.1',
            '203.0.113.1',
            '2001:0db8:85a3:0000:0000:8a2e:0370:7334',  # IPv6
            ''  # Empty is allowed
        ]
        
        for ip in valid_ips:
            newsletter_data['ip_address'] = ip
            serializer = NewsletterSerializer(data=newsletter_data)
            assert serializer.is_valid(), f"IP address '{ip}' should be valid"


@pytest.mark.django_db
class TestContactSerializerIntegration:
    """Integration tests for contact serializers working together."""
    
    def test_same_email_different_models(self):
        """Test that the same email can be used in both contact message and newsletter."""
        email = 'shared@example.com'
        
        # Create contact message
        message_data = {
            'name': 'Contact User',
            'email': email,
            'message': 'Contact message content'
        }
        
        message_serializer = ContactMessageSerializer(data=message_data)
        assert message_serializer.is_valid()
        message = message_serializer.save()
        
        # Create newsletter subscription with same email
        newsletter_data = {
            'email': email,
            'name': 'Newsletter User'
        }
        
        newsletter_serializer = NewsletterSerializer(data=newsletter_data)
        assert newsletter_serializer.is_valid()
        subscription = newsletter_serializer.save()
        
        # Both should exist independently
        assert message.email == email
        assert subscription.email == email
        assert ContactMessage.objects.filter(email=email).exists()
        assert Newsletter.objects.filter(email=email).exists()
    
    def test_multiple_contact_messages_same_email(self):
        """Test that multiple contact messages can have the same email."""
        email = 'repeat@example.com'
        
        # Create first message
        message1_data = {
            'name': 'User One',
            'email': email,
            'subject': 'general',
            'message': 'First message'
        }
        
        serializer1 = ContactMessageSerializer(data=message1_data)
        assert serializer1.is_valid()
        message1 = serializer1.save()
        
        # Create second message with same email
        message2_data = {
            'name': 'User Two',
            'email': email,
            'subject': 'project',
            'message': 'Second message'
        }
        
        serializer2 = ContactMessageSerializer(data=message2_data)
        assert serializer2.is_valid()
        message2 = serializer2.save()
        
        # Both messages should exist
        assert ContactMessage.objects.filter(email=email).count() == 2
        assert message1.email == email
        assert message2.email == email
    
    def test_contact_workflow_serialization(self):
        """Test typical contact workflow through serializers."""
        # Create initial contact message
        initial_data = {
            'name': 'Workflow User',
            'email': 'workflow@example.com',
            'subject': 'project',
            'message': 'Initial project inquiry'
        }
        
        serializer = ContactMessageSerializer(data=initial_data)
        assert serializer.is_valid()
        message = serializer.save()
        
        # Verify initial state
        assert message.status == 'new'
        
        # Update to 'read' status
        update_data = {'status': 'read'}
        serializer = ContactMessageSerializer(message, data=update_data, partial=True)
        assert serializer.is_valid()
        message = serializer.save()
        assert message.status == 'read'
        
        # Update to 'replied' status
        update_data = {'status': 'replied'}
        serializer = ContactMessageSerializer(message, data=update_data, partial=True)
        assert serializer.is_valid()
        message = serializer.save()
        assert message.status == 'replied'
        
        # Finally archive
        update_data = {'status': 'archived'}
        serializer = ContactMessageSerializer(message, data=update_data, partial=True)
        assert serializer.is_valid()
        message = serializer.save()
        assert message.status == 'archived'
    
    def test_newsletter_activation_workflow_serialization(self):
        """Test newsletter activation workflow through serializers."""
        # Create subscription
        initial_data = {
            'email': 'activation@example.com',
            'name': 'Activation User'
        }
        
        serializer = NewsletterSerializer(data=initial_data)
        assert serializer.is_valid()
        subscription = serializer.save()
        
        # Verify initial state (active by default)
        assert subscription.is_active is True
        
        # Deactivate
        update_data = {'is_active': False}
        serializer = NewsletterSerializer(subscription, data=update_data, partial=True)
        assert serializer.is_valid()
        subscription = serializer.save()
        assert subscription.is_active is False
        
        # Reactivate
        update_data = {'is_active': True}
        serializer = NewsletterSerializer(subscription, data=update_data, partial=True)
        assert serializer.is_valid()
        subscription = serializer.save()
        assert subscription.is_active is True