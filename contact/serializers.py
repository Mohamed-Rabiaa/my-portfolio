from rest_framework import serializers
from .models import ContactMessage, Newsletter


class ContactMessageSerializer(serializers.ModelSerializer):
    """Serializer for ContactMessage model"""
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
        # Get IP address and user agent from request context
        request = self.context.get('request')
        if request:
            validated_data['ip_address'] = self.get_client_ip(request)
            validated_data['user_agent'] = request.META.get('HTTP_USER_AGENT', '')
        
        return super().create(validated_data)
    
    def get_client_ip(self, request):
        """Get client IP address from request"""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip


class NewsletterSerializer(serializers.ModelSerializer):
    """Serializer for Newsletter model"""
    
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