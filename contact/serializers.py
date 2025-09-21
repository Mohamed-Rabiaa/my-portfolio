"""
Contact Serializers Module

This module contains Django REST Framework serializers for the contact application.
It provides serialization and validation for contact messages and newsletter subscriptions,
handling data conversion between Python objects and JSON format for API endpoints.

Classes:
    ContactMessageSerializer: Serializer for ContactMessage model
    NewsletterSerializer: Serializer for Newsletter model

Author: Your Name
Version: 1.0.0
"""

from rest_framework import serializers
from .models import ContactMessage, Newsletter


class ContactMessageSerializer(serializers.ModelSerializer):
    """
    Django REST Framework serializer for ContactMessage model.
    
    Handles serialization and validation of contact message data for API endpoints.
    Provides automatic validation for required fields and custom validation methods
    for email format and message content.
    
    Attributes:
        Meta: Configuration class defining model and field settings
        
    Methods:
        validate_email: Custom validation for email field
        validate_message: Custom validation for message content
        create: Custom creation method with additional processing
    """
    
    class Meta:
        """
        Meta configuration for ContactMessageSerializer.
        
        Defines the model to serialize and which fields to include/exclude
        from the serialization process.
        
        Attributes:
            model: The Django model to serialize (ContactMessage)
            fields: List of fields to include in serialization
            read_only_fields: Fields that cannot be modified via API
        """
        model = ContactMessage
        fields = ['id', 'name', 'email', 'phone', 'company', 'subject', 'message', 'status', 'created_at']
        read_only_fields = ['id', 'status', 'created_at']
    
    def validate_email(self, value):
        """
        Custom validation for email field.
        
        Ensures the email address is properly formatted and not from
        blocked domains or disposable email services.
        
        Args:
            value (str): The email address to validate
            
        Returns:
            str: The validated email address
            
        Raises:
            serializers.ValidationError: If email format is invalid or blocked
        """
        if not value:
            raise serializers.ValidationError("Email address is required.")
        
        # Convert to lowercase for consistency
        value = value.lower().strip()
        
        # Basic email format validation (additional to DRF's built-in validation)
        if '@' not in value or '.' not in value.split('@')[1]:
            raise serializers.ValidationError("Please enter a valid email address.")
        
        # Check for blocked domains (example implementation)
        blocked_domains = ['tempmail.com', 'guerrillamail.com', '10minutemail.com']
        domain = value.split('@')[1]
        if domain in blocked_domains:
            raise serializers.ValidationError("Email from this domain is not allowed.")
        
        return value
    
    def validate_message(self, value):
        """
        Custom validation for message content.
        
        Ensures the message meets minimum length requirements and
        doesn't contain spam-like content.
        
        Args:
            value (str): The message content to validate
            
        Returns:
            str: The validated message content
            
        Raises:
            serializers.ValidationError: If message is too short or contains spam
        """
        if not value or len(value.strip()) < 10:
            raise serializers.ValidationError("Message must be at least 10 characters long.")
        
        # Check for spam-like content (basic implementation)
        spam_keywords = ['viagra', 'casino', 'lottery', 'winner']
        message_lower = value.lower()
        for keyword in spam_keywords:
            if keyword in message_lower:
                raise serializers.ValidationError("Message contains inappropriate content.")
        
        return value.strip()
    
    def create(self, validated_data):
        """
        Custom creation method for ContactMessage instances.
        
        Handles the creation of new contact messages with additional
        processing such as IP address capture and user agent detection.
        
        Args:
            validated_data (dict): Validated data from the serializer
            
        Returns:
            ContactMessage: The created contact message instance
        """
        # Get request context for additional data
        request = self.context.get('request')
        if request:
            # Capture IP address
            x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
            if x_forwarded_for:
                validated_data['ip_address'] = x_forwarded_for.split(',')[0]
            else:
                validated_data['ip_address'] = request.META.get('REMOTE_ADDR')
            
            # Capture user agent
            validated_data['user_agent'] = request.META.get('HTTP_USER_AGENT', '')
        
        return super().create(validated_data)


class NewsletterSerializer(serializers.ModelSerializer):
    """
    Django REST Framework serializer for Newsletter model.
    
    Handles serialization and validation of newsletter subscription data
    for API endpoints. Provides validation for email uniqueness and
    subscription preferences.
    
    Attributes:
        Meta: Configuration class defining model and field settings
        
    Methods:
        validate_email: Custom validation for email field
        validate: Cross-field validation method
        create: Custom creation method with subscription handling
    """
    
    class Meta:
        """
        Meta configuration for NewsletterSerializer.
        
        Defines the model to serialize and which fields to include/exclude
        from the serialization process.
        
        Attributes:
            model: The Django model to serialize (Newsletter)
            fields: List of fields to include in serialization
            read_only_fields: Fields that cannot be modified via API
        """
        model = Newsletter
        fields = ['id', 'email', 'name', 'is_active', 'subscribed_at']
        read_only_fields = ['id', 'subscribed_at']
    
    def validate_email(self, value):
        """
        Custom validation for email field in newsletter subscriptions.
        
        Ensures the email address is valid and checks for existing
        active subscriptions to prevent duplicates.
        
        Args:
            value (str): The email address to validate
            
        Returns:
            str: The validated email address
            
        Raises:
            serializers.ValidationError: If email is invalid or already subscribed
        """
        if not value:
            raise serializers.ValidationError("Email address is required.")
        
        # Convert to lowercase for consistency
        value = value.lower().strip()
        
        # Check if email is already subscribed and active
        if Newsletter.objects.filter(email=value, is_active=True).exists():
            raise serializers.ValidationError("This email is already subscribed to our newsletter.")
        
        return value
    
    def validate(self, data):
        """
        Cross-field validation for newsletter subscription data.
        
        Performs validation that requires access to multiple fields
        or the entire data dictionary.
        
        Args:
            data (dict): Dictionary containing all field data
            
        Returns:
            dict: The validated data dictionary
            
        Raises:
            serializers.ValidationError: If cross-field validation fails
        """
        # Ensure name is provided if email is a business email
        email = data.get('email', '')
        name = data.get('name', '')
        
        # Check if it's a business email (contains company indicators)
        business_indicators = ['info@', 'contact@', 'admin@', 'support@']
        if any(indicator in email for indicator in business_indicators) and not name:
            raise serializers.ValidationError({
                'name': 'Name is required for business email addresses.'
            })
        
        return data
    
    def create(self, validated_data):
        """
        Custom creation method for Newsletter subscription instances.
        
        Handles the creation of new newsletter subscriptions with
        additional processing and reactivation of existing inactive subscriptions.
        
        Args:
            validated_data (dict): Validated data from the serializer
            
        Returns:
            Newsletter: The created or reactivated newsletter subscription instance
        """
        email = validated_data['email']
        
        # Check if there's an inactive subscription for this email
        try:
            existing_subscription = Newsletter.objects.get(email=email, is_active=False)
            # Reactivate existing subscription
            existing_subscription.is_active = True
            existing_subscription.name = validated_data.get('name', existing_subscription.name)
            existing_subscription.save()
            return existing_subscription
        except Newsletter.DoesNotExist:
            # Create new subscription
            request = self.context.get('request')
            if request:
                # Capture IP address for new subscriptions
                x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
                if x_forwarded_for:
                    validated_data['ip_address'] = x_forwarded_for.split(',')[0]
                else:
                    validated_data['ip_address'] = request.META.get('REMOTE_ADDR')
            
            return super().create(validated_data)