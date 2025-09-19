from django.db import models
from django.core.validators import EmailValidator


class ContactMessage(models.Model):
    """Model for contact form messages"""
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
        return f"{self.name} - {self.get_subject_display()}"

    @property
    def is_new(self):
        return self.status == 'new'


class Newsletter(models.Model):
    """Model for newsletter subscriptions"""
    email = models.EmailField(unique=True, validators=[EmailValidator()])
    name = models.CharField(max_length=100, blank=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        ordering = ['-subscribed_at']

    def __str__(self):
        return f"{self.email} ({'Active' if self.is_active else 'Inactive'})"
