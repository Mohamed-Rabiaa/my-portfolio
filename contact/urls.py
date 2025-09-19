from django.urls import path
from . import views

app_name = 'contact'

urlpatterns = [
    # Contact message endpoints
    path('messages/', views.ContactMessageCreateView.as_view(), name='message-create'),
    
    # Newsletter endpoints
    path('newsletter/subscribe/', views.NewsletterSubscribeView.as_view(), name='newsletter-subscribe'),
    path('newsletter/unsubscribe/', views.newsletter_unsubscribe, name='newsletter-unsubscribe'),
    
    # Statistics
    path('stats/', views.contact_stats, name='contact-stats'),
]