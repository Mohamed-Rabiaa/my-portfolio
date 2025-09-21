"""
Comprehensive pytest tests for contact application models.

This module provides thorough testing for all contact models including:
- ContactMessage model: contact form submissions, status workflow, validation
- Newsletter model: newsletter subscriptions, email validation, activation

Tests cover:
- Model field validation and constraints
- Choice field validation (subject categories, status workflow)
- Email field validation and uniqueness
- Model methods and properties
- String representations
- Model ordering and meta options
- IP address and user agent tracking
- Timestamp handling
"""

import pytest
from django.test import TestCase
from django.core.exceptions import ValidationError
from django.db import IntegrityError
from datetime import datetime
from contact.models import ContactMessage, Newsletter


@pytest.mark.django_db
class TestContactMessageModel:
    """Test cases for the ContactMessage model."""
    
    def test_contact_message_creation(self):
        """Test basic contact message creation with all fields."""
        message = ContactMessage.objects.create(
            name="John Doe",
            email="john@example.com",
            subject="general",
            message="Hello, this is a test message.",
            ip_address="192.168.1.1",
            user_agent="Mozilla/5.0 Test Browser"
        )
        
        assert message.name == "John Doe"
        assert message.email == "john@example.com"
        assert message.subject == "general"
        assert message.message == "Hello, this is a test message."
        assert message.status == "new"  # Default status
        assert message.ip_address == "192.168.1.1"
        assert message.user_agent == "Mozilla/5.0 Test Browser"
        assert message.created_at is not None
        assert message.updated_at is not None
        assert isinstance(message.created_at, datetime)
        assert isinstance(message.updated_at, datetime)
    
    def test_contact_message_required_fields(self):
        """Test contact message creation with only required fields."""
        message = ContactMessage.objects.create(
            name="Jane Smith",
            email="jane@example.com",
            message="Required fields only test."
        )
        
        assert message.name == "Jane Smith"
        assert message.email == "jane@example.com"
        assert message.message == "Required fields only test."
        assert message.subject == "general"  # Default subject
        assert message.status == "new"  # Default status
        assert message.ip_address == ""  # Optional field
        assert message.user_agent == ""  # Optional field
    
    def test_contact_message_subject_choices(self):
        """Test contact message subject choices validation."""
        valid_subjects = ['general', 'project', 'job', 'freelance', 'other']
        
        for subject in valid_subjects:
            message = ContactMessage.objects.create(
                name=f"Test User {subject}",
                email=f"test_{subject}@example.com",
                subject=subject,
                message=f"Test message for {subject} subject."
            )
            assert message.subject == subject
    
    def test_contact_message_status_choices(self):
        """Test contact message status choices validation."""
        valid_statuses = ['new', 'read', 'replied', 'archived']
        
        for status in valid_statuses:
            message = ContactMessage.objects.create(
                name=f"Test User {status}",
                email=f"test_{status}@example.com",
                message=f"Test message with {status} status.",
                status=status
            )
            assert message.status == status
    
    def test_contact_message_get_subject_display(self):
        """Test subject display names."""
        message = ContactMessage.objects.create(
            name="Test User",
            email="test@example.com",
            subject="project",
            message="Test message"
        )
        assert message.get_subject_display() == "Project Inquiry"
        
        message2 = ContactMessage.objects.create(
            name="Test User 2",
            email="test2@example.com",
            subject="freelance",
            message="Test message 2"
        )
        assert message2.get_subject_display() == "Freelance Work"
    
    def test_contact_message_get_status_display(self):
        """Test status display names."""
        message = ContactMessage.objects.create(
            name="Test User",
            email="test@example.com",
            message="Test message",
            status="read"
        )
        assert message.get_status_display() == "Read"
        
        message2 = ContactMessage.objects.create(
            name="Test User 2",
            email="test2@example.com",
            message="Test message 2",
            status="replied"
        )
        assert message2.get_status_display() == "Replied"
    
    def test_contact_message_is_new_property(self):
        """Test is_new property method."""
        # New message
        new_message = ContactMessage.objects.create(
            name="New User",
            email="new@example.com",
            message="New message",
            status="new"
        )
        assert new_message.is_new is True
        
        # Read message
        read_message = ContactMessage.objects.create(
            name="Read User",
            email="read@example.com",
            message="Read message",
            status="read"
        )
        assert read_message.is_new is False
        
        # Replied message
        replied_message = ContactMessage.objects.create(
            name="Replied User",
            email="replied@example.com",
            message="Replied message",
            status="replied"
        )
        assert replied_message.is_new is False
    
    def test_contact_message_string_representation(self):
        """Test contact message string representation."""
        message = ContactMessage.objects.create(
            name="Alice Johnson",
            email="alice@example.com",
            subject="job",
            message="Job inquiry message"
        )
        expected = "Alice Johnson - Job Inquiry"
        assert str(message) == expected
    
    def test_contact_message_ordering(self):
        """Test contact message ordering by created_at descending."""
        # Create messages with slight delay to ensure different timestamps
        import time
        
        message1 = ContactMessage.objects.create(
            name="First User",
            email="first@example.com",
            message="First message"
        )
        
        time.sleep(0.01)  # Small delay
        
        message2 = ContactMessage.objects.create(
            name="Second User",
            email="second@example.com",
            message="Second message"
        )
        
        messages = list(ContactMessage.objects.all())
        
        # Should be ordered by created_at descending (newest first)
        assert messages[0] == message2
        assert messages[1] == message1
    
    def test_contact_message_email_validation(self):
        """Test email field validation."""
        # Valid email should work
        message = ContactMessage.objects.create(
            name="Valid User",
            email="valid@example.com",
            message="Valid email test"
        )
        assert message.email == "valid@example.com"
        
        # Test with different valid email formats
        valid_emails = [
            "user@domain.com",
            "user.name@domain.co.uk",
            "user+tag@domain.org",
            "123@domain.net"
        ]
        
        for email in valid_emails:
            message = ContactMessage.objects.create(
                name="Test User",
                email=email,
                message="Email validation test"
            )
            assert message.email == email
    
    def test_contact_message_long_text_fields(self):
        """Test handling of long text in message field."""
        long_message = "A" * 2000  # Very long message
        
        message = ContactMessage.objects.create(
            name="Long Message User",
            email="long@example.com",
            message=long_message
        )
        
        assert message.message == long_message
        assert len(message.message) == 2000
    
    def test_contact_message_ip_address_formats(self):
        """Test different IP address formats."""
        ip_addresses = [
            "192.168.1.1",
            "10.0.0.1",
            "127.0.0.1",
            "2001:0db8:85a3:0000:0000:8a2e:0370:7334",  # IPv6
            ""  # Empty is allowed
        ]
        
        for ip in ip_addresses:
            message = ContactMessage.objects.create(
                name=f"IP Test User {len(ip)}",
                email=f"ip{len(ip)}@example.com",
                message="IP address test",
                ip_address=ip
            )
            assert message.ip_address == ip


@pytest.mark.django_db
class TestNewsletterModel:
    """Test cases for the Newsletter model."""
    
    def test_newsletter_creation(self):
        """Test basic newsletter subscription creation."""
        subscription = Newsletter.objects.create(
            email="subscriber@example.com",
            name="John Subscriber",
            ip_address="192.168.1.100"
        )
        
        assert subscription.email == "subscriber@example.com"
        assert subscription.name == "John Subscriber"
        assert subscription.is_active is True  # Default value
        assert subscription.ip_address == "192.168.1.100"
        assert subscription.subscribed_at is not None
        assert isinstance(subscription.subscribed_at, datetime)
    
    def test_newsletter_required_fields_only(self):
        """Test newsletter creation with only required email field."""
        subscription = Newsletter.objects.create(
            email="minimal@example.com"
        )
        
        assert subscription.email == "minimal@example.com"
        assert subscription.name == ""  # Optional field
        assert subscription.is_active is True  # Default
        assert subscription.ip_address == ""  # Optional field
    
    def test_newsletter_unique_email_constraint(self):
        """Test that newsletter emails must be unique."""
        Newsletter.objects.create(
            email="unique@example.com",
            name="First Subscriber"
        )
        
        with pytest.raises(IntegrityError):
            Newsletter.objects.create(
                email="unique@example.com",
                name="Second Subscriber"
            )
    
    def test_newsletter_email_validation(self):
        """Test email field validation for newsletter."""
        # Valid emails should work
        valid_emails = [
            "newsletter@example.com",
            "user.newsletter@domain.co.uk",
            "newsletter+tag@domain.org",
            "123newsletter@domain.net"
        ]
        
        for email in valid_emails:
            subscription = Newsletter.objects.create(
                email=email,
                name=f"Subscriber for {email}"
            )
            assert subscription.email == email
    
    def test_newsletter_is_active_default(self):
        """Test that newsletter subscriptions are active by default."""
        subscription = Newsletter.objects.create(
            email="active@example.com"
        )
        assert subscription.is_active is True
    
    def test_newsletter_is_active_false(self):
        """Test newsletter subscription with is_active set to False."""
        subscription = Newsletter.objects.create(
            email="inactive@example.com",
            is_active=False
        )
        assert subscription.is_active is False
    
    def test_newsletter_string_representation(self):
        """Test newsletter string representation."""
        # Active subscription
        active_subscription = Newsletter.objects.create(
            email="active@example.com",
            name="Active User",
            is_active=True
        )
        expected_active = "active@example.com (Active)"
        assert str(active_subscription) == expected_active
        
        # Inactive subscription
        inactive_subscription = Newsletter.objects.create(
            email="inactive@example.com",
            name="Inactive User",
            is_active=False
        )
        expected_inactive = "inactive@example.com (Inactive)"
        assert str(inactive_subscription) == expected_inactive
    
    def test_newsletter_ordering(self):
        """Test newsletter ordering by subscribed_at descending."""
        import time
        
        # Create subscriptions with slight delay
        subscription1 = Newsletter.objects.create(
            email="first@example.com",
            name="First Subscriber"
        )
        
        time.sleep(0.01)  # Small delay
        
        subscription2 = Newsletter.objects.create(
            email="second@example.com",
            name="Second Subscriber"
        )
        
        subscriptions = list(Newsletter.objects.all())
        
        # Should be ordered by subscribed_at descending (newest first)
        assert subscriptions[0] == subscription2
        assert subscriptions[1] == subscription1
    
    def test_newsletter_optional_name_field(self):
        """Test newsletter with and without name field."""
        # With name
        with_name = Newsletter.objects.create(
            email="withname@example.com",
            name="Named Subscriber"
        )
        assert with_name.name == "Named Subscriber"
        
        # Without name (blank)
        without_name = Newsletter.objects.create(
            email="noname@example.com",
            name=""
        )
        assert without_name.name == ""
        
        # Default (should be blank)
        default_name = Newsletter.objects.create(
            email="default@example.com"
        )
        assert default_name.name == ""
    
    def test_newsletter_ip_address_tracking(self):
        """Test IP address tracking for newsletter subscriptions."""
        subscription = Newsletter.objects.create(
            email="tracked@example.com",
            name="Tracked User",
            ip_address="203.0.113.1"
        )
        
        assert subscription.ip_address == "203.0.113.1"
        
        # Test with empty IP address
        subscription2 = Newsletter.objects.create(
            email="noip@example.com"
        )
        assert subscription2.ip_address == ""


@pytest.mark.django_db
class TestContactModelIntegration:
    """Integration tests for contact models working together."""
    
    def test_multiple_contact_messages_same_email(self):
        """Test that multiple contact messages can have the same email."""
        email = "repeat@example.com"
        
        message1 = ContactMessage.objects.create(
            name="User One",
            email=email,
            subject="general",
            message="First message"
        )
        
        message2 = ContactMessage.objects.create(
            name="User Two",
            email=email,
            subject="project",
            message="Second message"
        )
        
        # Both messages should exist with same email
        assert ContactMessage.objects.filter(email=email).count() == 2
        assert message1.email == email
        assert message2.email == email
    
    def test_contact_message_and_newsletter_same_email(self):
        """Test that contact message and newsletter can share the same email."""
        email = "shared@example.com"
        
        # Create contact message
        message = ContactMessage.objects.create(
            name="Contact User",
            email=email,
            message="Contact message"
        )
        
        # Create newsletter subscription with same email
        subscription = Newsletter.objects.create(
            email=email,
            name="Newsletter User"
        )
        
        # Both should exist independently
        assert message.email == email
        assert subscription.email == email
        assert ContactMessage.objects.filter(email=email).exists()
        assert Newsletter.objects.filter(email=email).exists()
    
    def test_contact_workflow_status_progression(self):
        """Test typical workflow progression of contact message status."""
        message = ContactMessage.objects.create(
            name="Workflow User",
            email="workflow@example.com",
            message="Test workflow message"
        )
        
        # Initially new
        assert message.status == "new"
        assert message.is_new is True
        
        # Mark as read
        message.status = "read"
        message.save()
        assert message.status == "read"
        assert message.is_new is False
        
        # Mark as replied
        message.status = "replied"
        message.save()
        assert message.status == "replied"
        assert message.is_new is False
        
        # Archive the message
        message.status = "archived"
        message.save()
        assert message.status == "archived"
        assert message.is_new is False
    
    def test_newsletter_activation_workflow(self):
        """Test newsletter activation/deactivation workflow."""
        subscription = Newsletter.objects.create(
            email="activation@example.com",
            name="Activation User"
        )
        
        # Initially active
        assert subscription.is_active is True
        
        # Deactivate
        subscription.is_active = False
        subscription.save()
        assert subscription.is_active is False
        
        # Reactivate
        subscription.is_active = True
        subscription.save()
        assert subscription.is_active is True