"""
Contact Application Serializers

This module contains serializers for the contact application, handling
data serialization and validation for contact messages and newsletter
subscriptions with enhanced functionality for client metadata capture.
"""

from rest_framework import serializers
from .models import ContactMessage, Newsletter


class ContactMessageSerializer(serializers.ModelSerializer):
    """
    Serializer for ContactMessage model with enhanced display fields and metadata capture.
    
    This serializer handles contact form submissions with automatic IP address
    and user agent detection for security and analytics purposes. It provides
    human-readable display fields for subject and status choices.
    
    Features:
    - Automatic IP address detection from various headers
    - User agent capture for client identification
    - Display fields for choice field values
    - Secure handling of sensitive metadata fields
    - Custom validation and creation logic
    
    Fields:
    - id: Unique identifier (read-only)
    - name: Contact person's name
    - email: Contact email address
    - subject: Message subject category
    - subject_display: Human-readable subject (read-only)
    - message: Message content
    - phone: Optional phone number
    - company: Optional company name
    - status: Message processing status (read-only)
    - status_display: Human-readable status (read-only)
    - created_at: Timestamp of message creation (read-only)
    """
    subject_display = serializers.CharField(source='get_subject_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = ContactMessage
        fields = [
            'id', 'name', 'email', 'subject', 'subject_display', 'message',
            'phone', 'company', 'status', 'status_display', 'created_at'
        ]
        extra_kwargs = {
            'status': {'read_only': True},
            'ip_address': {'write_only': True},
            'user_agent': {'write_only': True},
        }

    def create(self, validated_data):
        """
        Create a new ContactMessage instance with automatic metadata capture.
        
        This method automatically captures the client's IP address and user agent
        from the request context for security and analytics purposes. It handles
        various proxy configurations to accurately determine the client's IP.
        
        Args:
            validated_data (dict): Validated form data from the serializer
            
        Returns:
            ContactMessage: The created contact message instance
        """
        # Get IP address and user agent from request context
        request = self.context.get('request')
        if request:
            validated_data['ip_address'] = self.get_client_ip(request)
            validated_data['user_agent'] = request.META.get('HTTP_USER_AGENT', '')
        
        return super().create(validated_data)
    
    def get_client_ip(self, request):
        """
        Extract the client's IP address from the request.
        
        This method handles various proxy configurations and headers to accurately
        determine the client's real IP address, prioritizing X-Forwarded-For header
        for proxy setups and falling back to REMOTE_ADDR for direct connections.
        
        Args:
            request: The HTTP request object
            
        Returns:
            str: The client's IP address
        """
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class NewsletterSerializer(serializers.ModelSerializer):
    """
    Serializer for Newsletter model with subscription management features.
    
    This serializer handles newsletter subscription requests with automatic
    IP address tracking for analytics and security purposes. It manages
    subscription status and provides read-only access to sensitive fields.
    
    Features:
    - Automatic IP address capture during subscription
    - Read-only subscription status management
    - Secure handling of metadata fields
    - Subscription timestamp tracking
    
    Fields:
    - id: Unique identifier (read-only)
    - email: Subscriber's email address
    - name: Optional subscriber name
    - subscribed_at: Subscription timestamp (read-only)
    - is_active: Subscription status (read-only)
    
    Note:
    The ip_address field is write-only and automatically populated
    during the subscription process for security tracking.
    """
    
    class Meta:
        model = Newsletter
        fields = ['id', 'email', 'name', 'subscribed_at', 'is_active']
        extra_kwargs = {
            'is_active': {'read_only': True},
            'ip_address': {'write_only': True},
        }

    def create(self, validated_data):
        # Get IP address from request context
        request = self.context.get('request')
        if request:
            validated_data['ip_address'] = self.get_client_ip(request)
        
        return super().create(validated_data)
    
    def get_client_ip(self, request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip