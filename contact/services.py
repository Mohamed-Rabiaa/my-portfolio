"""
Service layer for contact functionality.

This module contains business logic for contact operations, separating concerns
from views and providing reusable methods for contact-related operations.
"""

import logging
import time
from typing import Optional, Dict, Any
from django.db.models import QuerySet
from django.utils import timezone
from django.core.mail import send_mail
from django.conf import settings
from django.core.exceptions import ValidationError

from .models import ContactMessage
from common.exceptions import (
    ValidationError as CustomValidationError,
    NotFoundError
)
from common.utils import validate_email, sanitize_html

# Initialize loggers
logger = logging.getLogger('contact')
performance_logger = logging.getLogger('performance')


class ContactService:
    """
    Service class for contact operations.
    
    Handles all business logic related to contact messages including creation,
    retrieval, email notifications, and spam prevention.
    """
    
    @staticmethod
    def create_contact_message(
        name: str,
        email: str,
        subject: str,
        message: str,
        phone: Optional[str] = None
    ) -> ContactMessage:
        """
        Create a new contact message with validation and email notification.
        
        Args:
            name: Sender's name
            email: Sender's email
            subject: Message subject
            message: Message content
            phone: Optional phone number
            
        Returns:
            Created contact message instance
            
        Raises:
            CustomValidationError: If validation fails
        """
        start_time = time.time()
        logger.info(f"Creating contact message from {email} with subject: {subject}")
        
        try:
            # Validate email format
            if not validate_email(email):
                logger.warning(f"Invalid email format: {email}")
                raise CustomValidationError("Invalid email format")
            
            # Sanitize inputs
            name = sanitize_html(name.strip())
            subject = sanitize_html(subject.strip())
            message = sanitize_html(message.strip())
            
            if phone:
                phone = sanitize_html(phone.strip())
            
            logger.debug(f"Inputs sanitized for contact message from {email}")
            
            # Validate required fields
            if not all([name, email, subject, message]):
                logger.warning(f"Missing required fields in contact message from {email}")
                raise CustomValidationError("All required fields must be provided")
            
            # Check message length
            if len(message) < 10:
                raise CustomValidationError("Message must be at least 10 characters long")
            
            if len(message) > 5000:
                raise CustomValidationError("Message must be less than 5000 characters")
            
            # Create the contact message
            contact_message = ContactMessage.objects.create(
                name=name,
                email=email,
                subject=subject,
                message=message,
                phone=phone,
                created_at=timezone.now()
            )
            
            logger.info(f"Contact message created with ID: {contact_message.id}")
            
            # Send notification email
            try:
                email_sent = ContactService._send_notification_email(contact_message)
                if email_sent:
                    logger.info(f"Notification email sent for contact message {contact_message.id}")
                else:
                    logger.warning(f"Failed to send notification email for contact message {contact_message.id}")
            except Exception as email_error:
                logger.error(f"Error sending notification email: {str(email_error)}", exc_info=True)
            
            execution_time = time.time() - start_time
            logger.info(f"Successfully created contact message from {email}")
            performance_logger.info(f"create_contact_message executed in {execution_time:.3f}s for {email}")
            
            return contact_message
            
        except CustomValidationError:
            execution_time = time.time() - start_time
            performance_logger.info(f"create_contact_message validation failed in {execution_time:.3f}s for {email}")
            raise
        except Exception as e:
            execution_time = time.time() - start_time
            logger.error(f"Error creating contact message from {email}: {str(e)}", exc_info=True)
            performance_logger.info(f"create_contact_message failed in {execution_time:.3f}s for {email}")
            raise
    
    @staticmethod
    def get_all_messages(read_only=None):
        """
        Get all contact messages with optional filtering and optimized queries.
        
        Args:
            read_only: Filter by read status (None for all)
            
        Returns:
            QuerySet of contact messages
        """
        queryset = ContactMessage.objects.all().order_by('-created_at')
        
        if read_only is not None:
            queryset = queryset.filter(is_read=read_only)
            
        return queryset
    
    @staticmethod
    def get_unread_messages():
        """
        Get all unread contact messages with optimized queries.
        
        Returns:
            QuerySet of unread contact messages
        """
        return ContactMessage.objects.filter(
            is_read=False
        ).order_by('-created_at')
    
    @staticmethod
    def mark_as_read(message: ContactMessage) -> ContactMessage:
        """
        Mark a contact message as read.
        
        Args:
            message: ContactMessage instance
            
        Returns:
            Updated contact message instance
        """
        message.is_read = True
        message.read_at = timezone.now()
        message.save()
        return message
    
    @staticmethod
    def get_message_by_id(message_id: int) -> ContactMessage:
        """
        Get a contact message by ID.
        
        Args:
            message_id: Message ID
            
        Returns:
            ContactMessage instance
            
        Raises:
            NotFoundError: If message doesn't exist
        """
        try:
            return ContactMessage.objects.get(id=message_id)
        except ContactMessage.DoesNotExist:
            raise NotFoundError(f"Contact message with ID {message_id} not found")
    
    @staticmethod
    def get_contact_stats() -> Dict[str, int]:
        """
        Get contact message statistics.
        
        Returns:
            Dictionary containing contact statistics
        """
        return {
            'total_messages': ContactMessage.objects.count(),
            'unread_messages': ContactMessage.objects.filter(is_read=False).count(),
            'read_messages': ContactMessage.objects.filter(is_read=True).count(),
            'messages_today': ContactMessage.objects.filter(
                created_at__date=timezone.now().date()
            ).count(),
        }
    
    @staticmethod
    def _send_notification_email(contact_message: ContactMessage) -> bool:
        """
        Send email notification for new contact message.
        
        Args:
            contact_message: ContactMessage instance
            
        Returns:
            True if email sent successfully, False otherwise
        """
        try:
            subject = f"New Contact Message: {contact_message.subject}"
            message_body = f"""
            New contact message received:
            
            Name: {contact_message.name}
            Email: {contact_message.email}
            Phone: {contact_message.phone or 'Not provided'}
            Subject: {contact_message.subject}
            
            Message:
            {contact_message.message}
            
            Received at: {contact_message.created_at}
            """
            
            send_mail(
                subject=subject,
                message=message_body,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.CONTACT_EMAIL],
                fail_silently=False,
            )
            return True
        except Exception as e:
            # Log the error in production
            print(f"Failed to send notification email: {e}")
            return False
    
    @staticmethod
    def delete_message(message: ContactMessage) -> bool:
        """
        Delete a contact message.
        
        Args:
            message: ContactMessage instance
            
        Returns:
            True if deleted successfully
        """
        message.delete()
        return True
    
    @staticmethod
    def bulk_mark_as_read(message_ids: list) -> int:
        """
        Mark multiple messages as read.
        
        Args:
            message_ids: List of message IDs
            
        Returns:
            Number of messages updated
        """
        return ContactMessage.objects.filter(
            id__in=message_ids,
            is_read=False
        ).update(
            is_read=True,
            read_at=timezone.now()
        )