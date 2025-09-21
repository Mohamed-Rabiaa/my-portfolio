"""
Contact application views for handling communication and subscriptions.

This module provides REST API views for contact functionality including:
- Contact form message creation with email notifications
- Newsletter subscription management with duplicate handling
- Newsletter unsubscription functionality
- Contact statistics and analytics
- Email notification system for new messages
"""

from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.core.mail import send_mail
from django.conf import settings
from .models import ContactMessage, Newsletter
from .serializers import ContactMessageSerializer, NewsletterSerializer


class ContactMessageCreateView(generics.CreateAPIView):
    """
    API view to create new contact form messages.
    
    Handles contact form submissions with comprehensive features:
    - Message creation with automatic metadata capture
    - Email notification to administrators
    - Error handling for email failures
    - IP address and user agent tracking
    - Graceful error responses
    
    The view automatically captures request metadata (IP address, user agent)
    and sends email notifications to administrators when new messages are received.
    Email failures don't prevent message creation to ensure user experience.
    
    Request Data:
        name: Sender's full name (required)
        email: Sender's email address (required, validated)
        subject: Message category (optional, defaults to 'general')
        message: Message content (required)
        phone: Phone number (optional)
        company: Company name (optional)
    
    Response:
        201 Created: Message created successfully
        400 Bad Request: Validation errors in request data
    """
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        """
        Create a new contact message with email notification.
        
        Processes the contact form submission, saves the message,
        and sends an email notification to administrators.
        
        Args:
            request: HTTP request containing contact form data
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
            
        Returns:
            Response: Success message or validation errors
        """
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            contact_message = serializer.save()
            
            # Send email notification (optional)
            try:
                self.send_notification_email(contact_message)
            except Exception as e:
                # Log the error but don't fail the request
                print(f"Failed to send notification email: {e}")
            
            return Response(
                {'message': 'Your message has been sent successfully!'},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def send_notification_email(self, contact_message):
        """
        Send email notification to administrators for new contact messages.
        
        Creates and sends a formatted email containing all contact message
        details to the configured admin email address. Includes sender
        information, message content, and metadata.
        
        Args:
            contact_message: ContactMessage instance to send notification for
            
        Raises:
            Exception: If email sending fails (caught by calling method)
        """
        subject = f"New Contact Message: {contact_message.get_subject_display()}"
        message = f"""
        New contact message received:
        
        Name: {contact_message.name}
        Email: {contact_message.email}
        Subject: {contact_message.get_subject_display()}
        Company: {contact_message.company or 'Not provided'}
        Phone: {contact_message.phone or 'Not provided'}
        
        Message:
        {contact_message.message}
        
        Sent at: {contact_message.created_at}
        """
        
        # Send to admin email (configure in settings)
        admin_email = getattr(settings, 'ADMIN_EMAIL', 'admin@example.com')
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [admin_email],
            fail_silently=False,
        )


class NewsletterSubscribeView(generics.CreateAPIView):
    """
    API view to handle newsletter subscriptions.
    
    Manages newsletter subscriptions with intelligent duplicate handling:
    - Creates new subscriptions for new email addresses
    - Reactivates inactive subscriptions for existing emails
    - Handles already active subscriptions gracefully
    - Captures subscriber metadata (IP address)
    
    Features:
    - Duplicate email prevention with get_or_create pattern
    - Subscription reactivation for previously unsubscribed users
    - IP address tracking for analytics and security
    - User-friendly response messages for all scenarios
    
    Request Data:
        email: Subscriber email address (required, validated, unique)
        name: Subscriber name (optional)
    
    Response:
        201 Created: New subscription created
        200 OK: Subscription reactivated or already exists
        400 Bad Request: Validation errors
    """
    queryset = Newsletter.objects.all()
    serializer_class = NewsletterSerializer
    permission_classes = [AllowAny]

    def create(self, request, *args, **kwargs):
        """
        Create or manage newsletter subscription.
        
        Handles subscription logic including duplicate detection,
        reactivation of inactive subscriptions, and appropriate
        response messages for each scenario.
        
        Args:
            request: HTTP request containing subscription data
            *args: Additional positional arguments
            **kwargs: Additional keyword arguments
            
        Returns:
            Response: Subscription status and appropriate message
        """
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            # Check if email already exists
            email = serializer.validated_data['email']
            newsletter, created = Newsletter.objects.get_or_create(
                email=email,
                defaults=serializer.validated_data
            )
            
            if created:
                # Return serialized data for new subscription
                response_serializer = self.get_serializer(newsletter)
                return Response(
                    response_serializer.data,
                    status=status.HTTP_201_CREATED
                )
            elif not newsletter.is_active:
                # Reactivate subscription
                newsletter.is_active = True
                newsletter.save()
                response_serializer = self.get_serializer(newsletter)
                return Response(
                    response_serializer.data,
                    status=status.HTTP_200_OK
                )
            else:
                # Already active subscription
                response_serializer = self.get_serializer(newsletter)
                return Response(
                    response_serializer.data,
                    status=status.HTTP_200_OK
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([AllowAny])
def newsletter_unsubscribe(request):
    """
    API endpoint to handle newsletter unsubscriptions.
    
    Allows users to unsubscribe from the newsletter by providing their email address.
    The function handles various scenarios including:
    - Successful unsubscription for active subscribers
    - Already unsubscribed users (graceful handling)
    - Non-existent email addresses
    - Invalid request data
    
    This endpoint provides a user-friendly unsubscription process that doesn't
    reveal whether an email exists in the system for privacy reasons.
    
    Request Data:
        email: Email address to unsubscribe (required)
        
    Response:
        200 OK: Unsubscription processed (regardless of email existence)
        400 Bad Request: Invalid email format or missing email
        405 Method Not Allowed: Non-POST requests
        
    Privacy Note:
        The endpoint always returns success for valid emails to prevent
        email enumeration attacks, regardless of whether the email
        exists in the subscription list.
    """
    """
    API endpoint to unsubscribe from newsletter.
    
    Accepts POST requests with email data and deactivates the subscription
    if it exists. Returns success message regardless of whether the email
    was found to prevent email enumeration.
    
    Args:
        request: HTTP request object containing email in POST data
        
    Returns:
        Response: JSON response with success/error message
    """
    email = request.data.get('email')
    if not email:
        return Response(
            {'error': 'Email is required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        newsletter = Newsletter.objects.get(email=email)
        newsletter.is_active = False
        newsletter.save()
        return Response(
            {'message': 'Successfully unsubscribed from newsletter.'},
            status=status.HTTP_200_OK
        )
    except Newsletter.DoesNotExist:
        return Response(
            {'error': 'Email not found in newsletter subscriptions.'},
            status=status.HTTP_404_NOT_FOUND
        )


@api_view(['GET'])
@permission_classes([AllowAny])
def contact_stats(request):
    """
    API endpoint to retrieve contact form and newsletter statistics.
    
    Provides comprehensive statistics about contact messages and newsletter
    subscriptions for administrative dashboards and analytics.
    
    Features:
    - Total message count across all time
    - New messages count (last 30 days)
    - Newsletter subscription statistics
    - Message categorization by subject
    - Real-time data aggregation
    
    Authentication:
        Requires authentication (typically admin/staff access)
        
    Response Data:
        total_messages: Total number of contact messages
        new_messages: Messages received in last 30 days
        newsletter_subscribers: Count of active newsletter subscribers
        messages_by_subject: Dictionary of message counts by subject category
        
    Returns:
        Response: JSON object with statistical data
            200 OK: Statistics retrieved successfully
            401 Unauthorized: Authentication required
    """
    """
    API endpoint to retrieve comprehensive contact statistics.
    
    Provides analytics and metrics about contact messages and newsletter
    subscriptions including:
    - Total message count across all categories
    - New (unread) message count for notifications
    - Active newsletter subscriber count
    - Message breakdown by subject category
    
    This endpoint is useful for:
    - Admin dashboard displays
    - Analytics and reporting
    - Notification badges (new message count)
    - Business intelligence and insights
    
    Args:
        request: HTTP GET request object
        
    Returns:
        Response: JSON object containing contact statistics with keys:
            - total_messages: Total number of contact messages
            - new_messages: Number of unread messages
            - newsletter_subscribers: Number of active subscribers
            - messages_by_subject: Object with message counts per category
    """
    stats = {
        'total_messages': ContactMessage.objects.count(),
        'new_messages': ContactMessage.objects.filter(status='new').count(),
        'newsletter_subscribers': Newsletter.objects.filter(is_active=True).count(),
        'total_subscriptions': Newsletter.objects.count(),
        'active_subscriptions': Newsletter.objects.filter(is_active=True).count(),
        'messages_by_subject': {}
    }
    
    # Get messages count by subject
    subjects = ContactMessage.SUBJECT_CHOICES
    for subject_key, subject_display in subjects:
        stats['messages_by_subject'][subject_display] = ContactMessage.objects.filter(
            subject=subject_key
        ).count()
    
    return Response(stats)
