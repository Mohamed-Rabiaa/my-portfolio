"""
Contact application models for managing communication and subscriptions.

This module defines models for handling:
- Contact form messages with categorization and status tracking
- Newsletter subscriptions with activation management
- Message metadata including IP addresses and user agents for security
- Comprehensive status workflow for message management
"""

from django.db import models
from django.core.validators import EmailValidator


class ContactMessage(models.Model):
    """
    Model for storing and managing contact form messages.
    
    Handles all incoming contact form submissions with comprehensive
    categorization and status tracking. Provides:
    - Subject categorization for better organization
    - Status workflow (new -> read -> replied -> archived)
    - Contact information with optional phone and company
    - Security metadata (IP address, user agent)
    - Timestamp tracking for creation and updates
    
    Subject Categories:
        - general: General inquiries and questions
        - project: Project collaboration requests
        - job: Job opportunity discussions
        - freelance: Freelance work proposals
        - other: Miscellaneous topics
    
    Status Workflow:
        - new: Newly received message (default)
        - read: Message has been viewed
        - replied: Response has been sent
        - archived: Message archived for record keeping
    
    Attributes:
        name: Sender's full name (required)
        email: Sender's email address with validation
        subject: Message category from predefined choices
        message: Full message content
        phone: Optional phone number
        company: Optional company/organization name
        status: Current message status in workflow
        ip_address: Sender's IP address for security tracking
        user_agent: Browser/client information
        created_at: Message submission timestamp
        updated_at: Last modification timestamp
    """
    SUBJECT_CHOICES = [
        ('general', 'General Inquiry'),
        ('project', 'Project Collaboration'),
        ('job', 'Job Opportunity'),
        ('freelance', 'Freelance Work'),
        ('other', 'Other'),
    ]

    STATUS_CHOICES = [
        ('new', 'New'),
        ('read', 'Read'),
        ('replied', 'Replied'),
        ('archived', 'Archived'),
    ]

    name = models.CharField(max_length=100)
    email = models.EmailField(validators=[EmailValidator()])
    subject = models.CharField(max_length=20, choices=SUBJECT_CHOICES, default='general')
    message = models.TextField()
    phone = models.CharField(max_length=20, blank=True)
    company = models.CharField(max_length=100, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='new')
    ip_address = models.GenericIPAddressField(null=True, blank=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        """
        String representation showing sender name and subject category.
        
        Returns:
            str: Formatted string with name and human-readable subject
        """
        return f"{self.name} - {self.get_subject_display()}"

    @property
    def is_new(self):
        """
        Check if the message is in 'new' status.
        
        Useful for highlighting unread messages in admin interfaces
        and filtering new messages for notifications.
        
        Returns:
            bool: True if message status is 'new', False otherwise
        """
        return self.status == 'new'


class Newsletter(models.Model):
    """
    Model for managing newsletter subscriptions.
    
    Handles email newsletter subscriptions with activation management.
    Provides:
    - Unique email constraint to prevent duplicates
    - Optional subscriber name for personalization
    - Activation status for subscription management
    - IP address tracking for security and analytics
    - Subscription timestamp tracking
    
    Features:
    - Automatic subscription timestamp on creation
    - Active/inactive status for easy subscription management
    - IP address logging for security and geographic analytics
    - Unique email constraint prevents duplicate subscriptions
    
    Attributes:
        email: Subscriber's email address (unique, validated)
        name: Optional subscriber name for personalization
        subscribed_at: Subscription timestamp (auto-generated)
        is_active: Subscription status (active/inactive)
        ip_address: Subscriber's IP address for tracking
    """
    email = models.EmailField(unique=True, validators=[EmailValidator()])
    name = models.CharField(max_length=100, blank=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-subscribed_at']

    def __str__(self):
        """
        String representation showing email and activation status.
        
        Returns:
            str: Formatted string with email and active/inactive status
        """
        return f"{self.email} ({'Active' if self.is_active else 'Inactive'})"
