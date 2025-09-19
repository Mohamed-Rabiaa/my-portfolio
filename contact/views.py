from rest_framework import generics, status
from rest_framework.decorators import api_view
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
from .models import ContactMessage, Newsletter
from .serializers import ContactMessageSerializer, NewsletterSerializer


class ContactMessageCreateView(generics.CreateAPIView):
    """Create a new contact message"""
    queryset = ContactMessage.objects.all()
    serializer_class = ContactMessageSerializer

    def create(self, request, *args, **kwargs):
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
        """Send email notification for new contact message"""
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
    """Subscribe to newsletter"""
    queryset = Newsletter.objects.all()
    serializer_class = NewsletterSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={'request': request})
        if serializer.is_valid():
            # Check if email already exists
            email = serializer.validated_data['email']
            newsletter, created = Newsletter.objects.get_or_create(
                email=email,
                defaults=serializer.validated_data
            )
            
            if created:
                return Response(
                    {'message': 'Successfully subscribed to newsletter!'},
                    status=status.HTTP_201_CREATED
                )
            elif not newsletter.is_active:
                # Reactivate subscription
                newsletter.is_active = True
                newsletter.save()
                return Response(
                    {'message': 'Newsletter subscription reactivated!'},
                    status=status.HTTP_200_OK
                )
            else:
                return Response(
                    {'message': 'Email is already subscribed to newsletter.'},
                    status=status.HTTP_200_OK
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def newsletter_unsubscribe(request):
    """Unsubscribe from newsletter"""
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
def contact_stats(request):
    """Get contact statistics"""
    stats = {
        'total_messages': ContactMessage.objects.count(),
        'new_messages': ContactMessage.objects.filter(status='new').count(),
        'newsletter_subscribers': Newsletter.objects.filter(is_active=True).count(),
        'messages_by_subject': {}
    }
    
    # Get messages count by subject
    subjects = ContactMessage.SUBJECT_CHOICES
    for subject_key, subject_display in subjects:
        stats['messages_by_subject'][subject_display] = ContactMessage.objects.filter(
            subject=subject_key
        ).count()
    
    return Response(stats)
