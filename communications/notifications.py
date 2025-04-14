from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification
from django.utils.timezone import now
from datetime import timedelta
from django.http import JsonResponse
from .serializers import *
from rest_framework.permissions import IsAuthenticated
from rest_framework import generics, filters, status
from rest_framework.response import Response

    
from datetime import timedelta
from django.utils.timezone import now
from channels.layers import get_channel_layer


from .views import *





def new_plan_purchased(business):
    """
    Function to handle plan purchase notifications.
    """
    # print('business:', business, 'from new_plan_purchased function')
    # title = f"Plan {business.plan_variant.plan.name} purchased successfully!"
    # duration_days = int(business.plan_variant.duration)
    # expiry_date = now() + timedelta(days=duration_days)

    # message = (
    #     f"Your new plan {business.plan_variant.plan.plan_name} has been purchased successfully! "
    #     f"The plan will be active from {now().strftime('%Y-%m-%d %H:%M:%S')} "
    #     f"and will expire on {expiry_date.strftime('%Y-%m-%d %H:%M:%S')}."
    # )    
    
    data = {
        'message': 'message',
        'title': 'title',
        'type': 'plan_purchase',
        'business': business,  # Add business info if needed
        'user': business.user,
    }
     
    
    return  notify_user(data)  

def plan_purchase_failed(business, error_message):
    """
    Function to handle failed plan purchase notifications.
    """
    title = "Plan purchase failed"
    message = (
        f"Failed to purchase plan {business.plan_varient.plan.plan_name}. "
        f"Reason: {error_message}. Please try again or contact support."
    )
    
    data = {
        'message': message,
        'title': title,
        'type': 'plan_purchase_failed',
        'business': business,
        'user': business.user,
    }

    return  notify_user(data)  


def amount_refunded(business, amount, reason):
    """
    Function to handle amount refund notifications.
    """
    title = "Amount refunded"
    message = (
        f"An amount of {amount} has been refunded to your account. "
        f"Reason: {reason}. Please check your payment method for confirmation."
    )
    
    data = {
        'message': message,
        'title': title,
        'type': 'amount_refunded',
        'business': business,
        'user': business.user,
    }
    
    return notify_user(data) 

def plan_expired(business):
    """
    Function to handle plan expiration notifications.
    """
    title = "Plan expired"
    message = (
        f"Your plan {business.plan_varient.plan.plan_name} has expired. "
        f"Please renew your plan to continue using premium features."
    )
    
    data = {
        'message': message,
        'title': title,
        'type': 'plan_expired',
        'business': business,
        'user': business.user,
    }
    
    return notify_user(data) 

def plan_renewed(business):
    """
    Function to handle plan renewal notifications.
    """
    duration_days = int(business.plan_varient.duration)
    expiry_date = now() + timedelta(days=duration_days)
    
    title = "Plan renewed successfully"
    message = (
        f"Your plan {business.plan_varient.plan.plan_name} has been renewed successfully! "
        f"The renewed plan will expire on {expiry_date.strftime('%Y-%m-%d %H:%M:%S')}."
    )
    
    data = {
        'message': message,
        'title': title,
        'type': 'plan_renewed',
        'business': business,
        'user': business.user,
    }
    
    return notify_user(data) 

def business_updates(business, update_message):
    """
    Function to handle business update notifications.
    """
    title = "Business update"
    message = f"Update regarding your business: {update_message}"
    
    data = {
        'message': message,
        'title': title,
        'type': 'business_updates',
        'business': business,
        'user': business.user,
    }
    
    return notify_user(data) 

def business_verified(business):
    """
    Function to handle business verification notifications.
    """
    title = "Business verified"
    message = "Congratulations! Your business has been successfully verified."
    
    data = {
        'message': message,
        'title': title,
        'type': 'business_verified',
        'business': business,
        'user': business.user,
    }
    
    return notify_user(data) 

def visit_report(business, visit_details):
    """
    Function to handle visit report notifications.
    """
    title = "New visit report"
    message = (
        f"A new visit has been recorded for your business. "
        f"Details: {visit_details}"
    )
    
    data = {
        'message': message,
        'title': title,
        'type': 'visit_report',
        'business': business,
        'user': business.user,
    }
    
    return notify_user(data) 

def enquiry_report(business, enquiry_details):
    """
    Function to handle enquiry report notifications.
    """
    title = "New enquiry"
    message = (
        f"A new enquiry has been received for your business. "
        f"Details: {enquiry_details}"
    )
    
    data = {
        'message': message,
        'title': title,
        'type': 'enquiry_report',
        'business': business,
        'user': business.user,
    }
    
    return notify_user(data) 

# Additional suggested notification types

def payment_reminder(business, days_remaining):
    """
    Function to handle payment reminder notifications.
    """
    title = "Payment reminder"
    message = (
        f"Your plan will expire in {days_remaining} days. "
        "Please renew to avoid service interruption."
    )
    
    data = {
        'message': message,
        'title': title,
        'type': 'payment_reminder',
        'business': business,
        'user': business.user,
    }
    
    return notify_user(data) 

def new_feature_announcement(business, feature_details):
    """
    Function to handle new feature announcements.
    """
    title = "New feature available"
    message = (
        f"A new feature is now available: {feature_details}. "
        "Check it out in your dashboard!"
    )
    
    data = {
        'message': message,
        'title': title,
        'type': 'new_feature',
        'business': business,
        'user': business.user,
    }
    
    return notify_user(data) 

def support_ticket_update(business, ticket_id, status):
    """
    Function to handle support ticket updates.
    """
    title = "Support ticket update"
    message = (
        f"Your support ticket #{ticket_id} has been updated. "
        f"Current status: {status}"
    )
    
    data = {
        'message': message,
        'title': title,
        'type': 'support_ticket_update',
        'business': business,
        'user': business.user,
    }
    
    return notify_user(data) 

def system_maintenance_notice(business, maintenance_time):
    """
    Function to handle system maintenance notifications.
    """
    title = "Scheduled maintenance"
    message = (
        f"The system will be undergoing maintenance on {maintenance_time}. "
        "Please plan your activities accordingly."
    )
    
    data = {
        'message': message,
        'title': title,
        'type': 'system_maintenance',
        'business': business,
        'user': business.user,
    }
    
    return notify_user(data) 