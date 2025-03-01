"""
Celery tasks for the bookings app.
"""
import logging

from celery import shared_task
from django.conf import settings
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils.translation import gettext_lazy as _

logger = logging.getLogger(__name__)


@shared_task
def send_booking_confirmation(booking_id):
    """
    Send a confirmation email for a booking.
    
    Args:
        booking_id: The ID of the booking to confirm.
    """
    from booking.apps.bookings.models import Booking
    
    try:
        booking = Booking.objects.select_related('user', 'facility').get(pk=booking_id)
        
        # Prepare the email
        subject = _('Booking Confirmation: %(title)s') % {'title': booking.title}
        
        # Render the email template
        email_context = {
            'booking': booking,
            'user': booking.user,
        }
        html_message = render_to_string('bookings/emails/booking_confirmation.html', email_context)
        plain_message = render_to_string('bookings/emails/booking_confirmation_plain.txt', email_context)
        
        # Send the email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Booking confirmation email sent for booking ID: {booking_id}")
        return True
        
    except Booking.DoesNotExist:
        logger.error(f"Failed to send booking confirmation: Booking {booking_id} does not exist")
        return False
    except Exception as e:
        logger.error(f"Failed to send booking confirmation for booking {booking_id}: {str(e)}")
        return False


@shared_task
def send_booking_cancellation(booking_id):
    """
    Send a cancellation email for a booking.
    
    Args:
        booking_id: The ID of the booking that was cancelled.
    """
    from booking.apps.bookings.models import Booking
    
    try:
        booking = Booking.objects.select_related('user', 'facility').get(pk=booking_id)
        
        # Prepare the email
        subject = _('Booking Cancellation: %(title)s') % {'title': booking.title}
        
        # Render the email template
        email_context = {
            'booking': booking,
            'user': booking.user,
        }
        html_message = render_to_string('bookings/emails/booking_cancellation.html', email_context)
        plain_message = render_to_string('bookings/emails/booking_cancellation_plain.txt', email_context)
        
        # Send the email
        send_mail(
            subject=subject,
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[booking.user.email],
            html_message=html_message,
            fail_silently=False,
        )
        
        logger.info(f"Booking cancellation email sent for booking ID: {booking_id}")
        return True
        
    except Booking.DoesNotExist:
        logger.error(f"Failed to send booking cancellation: Booking {booking_id} does not exist")
        return False
    except Exception as e:
        logger.error(f"Failed to send booking cancellation for booking {booking_id}: {str(e)}")
        return False


@shared_task
def send_booking_reminders():
    """
    Send reminder emails for upcoming bookings.
    This task should be scheduled to run daily.
    """
    from booking.apps.bookings.models import Booking
    from django.utils import timezone
    
    # Get bookings starting tomorrow
    tomorrow = timezone.now().date() + timezone.timedelta(days=1)
    
    try:
        # Find confirmed bookings for tomorrow
        bookings = Booking.objects.filter(
            status='confirmed',
            start_time__date=tomorrow
        ).select_related('user', 'facility')
        
        for booking in bookings:
            try:
                # Prepare the email
                subject = _('Reminder: Your booking tomorrow - %(title)s') % {'title': booking.title}
                
                # Render the email template
                email_context = {
                    'booking': booking,
                    'user': booking.user,
                }
                html_message = render_to_string('bookings/emails/booking_reminder.html', email_context)
                plain_message = render_to_string('bookings/emails/booking_reminder_plain.txt', email_context)
                
                # Send the email
                send_mail(
                    subject=subject,
                    message=plain_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[booking.user.email],
                    html_message=html_message,
                    fail_silently=False,
                )
                
                logger.info(f"Booking reminder email sent for booking ID: {booking.id}")
                
            except Exception as e:
                logger.error(f"Failed to send reminder for booking {booking.id}: {str(e)}")
        
        return True
        
    except Exception as e:
        logger.error(f"Failed to process booking reminders: {str(e)}")
        return False
