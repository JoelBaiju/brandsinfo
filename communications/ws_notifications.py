
from datetime import timedelta
from django.utils.timezone import now




from django.shortcuts import render

from channels.layers import get_channel_layer
from asgiref.sync import async_to_sync
from .models import Notification
from .serializers import *
from usershome.models import PhonePeTransaction
from usershome.Tools_Utils.payment_utils import generate_invoice_pdf
from celery import shared_task

@shared_task
def notify_user(data,extras=None):
    print('notiiiiiiii')
    message         = data['message'] 
    title           = data['title']
    ntype           = data['type']
    buisness_name   = data['buisness_name'] 
    buisness_id     = data['buisness_id'] 
    user           = data['user']

    print("task sending notification recieved ",data)
    
    
    
    channel_layer = get_channel_layer()
    group_name = f"user_{user}"

    async_to_sync(channel_layer.group_send)(
        group_name,
        {   
            "type": "send_notification",  # This maps to the `send_notification` method in the consumer
            "message": message,
            "timestamp": now().isoformat(),  # or str(now()) for simplicity
            "title": title, 
            "ntype": ntype,
            "business": buisness_name,  # Assuming you want to send the business name
            "business_id": buisness_id,  # Assuming you want to send the business ID
            "extras":extras
        }
    )
    
    return {"sent": True}




def new_plan_purchased(buisness):   
    print('buisness:', buisness, 'from new_plan_purchased function')
    title = f"Plan {buisness.plan_variant.plan.name} purchased successfully!"
    duration_days = int(buisness.plan_variant.duration)
    expiry_date = now() + timedelta(days=duration_days)

    message = (
        f"Your new plan {buisness.plan_variant.plan.plan_name} has been purchased successfully! "
        f"The plan will be active from {now().strftime('%Y-%m-%d %H:%M:%S')} "
        f"and will expire on {expiry_date.strftime('%Y-%m-%d %H:%M:%S')}."
    )    
    title = "Plan purchased successfully"
    noti = Notification.objects.create(    
        user=buisness.user,
        message=message,
        title=title,
        ntype=Notification.NotificationType.PLAN_PURCHASED,
        buisness=buisness,
    )
        
    
    data = {
        'message': message,
        'title': title,
        'type': noti.ntype,
        'buisness_name': buisness.name,  
        'buisness_id': buisness.id,  
        'user': buisness.user.username,
    }
     
    
    notify_user.delay(data=data , extras ={'invoice': generate_invoice_pdf(buisness.order_id)})  
    return True










def payment_status_update(order_id,):
    try:
        tnx = PhonePeTransaction.objects.get(order_id=order_id)
    except :
        print('here is the issue the order id is going mad')
    buisness = tnx.buisness
    print('notifiation for payment status update: was calledddddddddd' 'from payment_status_update function')

    print(buisness)
    plan = tnx.plan
    if tnx.status == 'COMPLETED':
        title = "Payment Completed"
        message = ( 
            f"Your payment for plan {plan.plan_name} has been processed successfully! "
            "Thank you for your purchase."
        )
    elif tnx.status == 'FAILED':
        title = "Payment Failed"
        message = (
            f"Your payment for plan {plan.plan_name} has failed."
            "Please try again or contact support."
        )
    elif tnx.status == 'PENDING':       
        title = "Payment Pending"
        message = (
            f"Your payment for plan {plan.plan_name} is pending. "
            "Please check your payment method for confirmation."
        )
    
    noti = Notification.objects.create(    
        user=buisness.user,
        message=message,
        title=title,
        ntype=Notification.NotificationType.PAYMENT_STATUS,
        buisness=buisness,
        order_id=order_id,  # Store the order ID in the notification
    )
    data = {
        'message': message,
        'title': title,
        'type': noti.ntype,
        'buisness_name': buisness.name,  
        'buisness_id': buisness.id,  
        'user': buisness.user.username,
    }

    notify_user.delay(data=data , extras = {'invoice' : generate_invoice_pdf(tnx.order_id),'status':tnx.status})
    return True














def amount_refunded(buisness, amount, reason):
    """
    Function to handle amount refund notifications.
    """
    title = "Amount refunded"
    message = (
        f"An amount of {amount} has been refunded to your account. "
        f"Reason: {reason}. Please check your payment method for confirmation."
    )
    
    
    noti = Notification.objects.create(    
        user=buisness.user,
        message=message,
        title=title,
        ntype=Notification.NotificationType.AMOUNT_REFUNDED,
        buisness=buisness,
    )
        
    
    data = {
        'message': message,
        'title': title,
        'type': noti.ntype,
        'buisness_name': buisness.name,  
        'buisness_id': buisness.id,  
        'user': buisness.user.username,
    }
    
    notify_user.delay(data) 
    return True


def plan_expired(buisness):
    """
    Function to handle plan expiration notifications.
    """ 
    title = "Plan expired"
    message = (
        f"Your plan {buisness.plan_variant.plan.plan_name} has expired. "
        f"Please renew your plan to continue using premium features."
    )
    
    noti = Notification.objects.create(    
        user=buisness.user,
        message=message,
        title=title,
        ntype=Notification.NotificationType.PLAN_EXPIRED,
        buisness=buisness,
    )
    noti.save()
        
    
    data = {
        'message': message,
        'title': title,
        'type': noti.ntype,
        'buisness_name': buisness.name,  
        'buisness_id': buisness.id,  
        'user': buisness.user.username,
    }
    
    notify_user.delay(data) 
    return True




def business_updates(buisness, update_message):
    """
    Function to handle business update notifications.
    """ 
    title = "Business update"
    message = f"Update regarding your business: {update_message}"
    noti = Notification.objects.create(    
        user=buisness.user,
        message=message,
        title=title,
        ntype=Notification.NotificationType.BUISNESS_UPDATES,
        buisness=buisness,
    )
    data = {
        'message': message,
        'title': title,
        'type': noti.ntype,
        'buisness_name': buisness.name,  
        'buisness_id': buisness.id,  
        'user': buisness.user.username,
    }
   
        
    
    
    notify_user.delay(data) 
    return True

def business_verified(buisness):
    """
    Function to handle business verification notifications.
    """
    title = "Business verified"
    message = "Congratulations! Your business has been successfully verified."
    noti = Notification.objects.create(    
        user=buisness.user,
        message=message,
        title=title,
        ntype=Notification.NotificationType.BI_VERIFIED,
        buisness=buisness,
    )
    data = {
        'message': message,
        'title': title,
        'type': noti.ntype,
        'buisness_name': buisness.name,  
        'buisness_id': buisness.id,  
        'user': buisness.user.username,
    }

    notify_user.delay(data) 
    return True

def visit_report(buisness, visit_details):
    """
    Function to handle visit report notifications.
    """
    title = "New visit report"
    message = (
        f"A new visit has been recorded for your business. "
        f"Details: {visit_details}"
    )
    noti = Notification.objects.create(    
        user=buisness.user,
        message=message,
        title=title,
        ntype=Notification.NotificationType.VISIT_REPORT,
        buisness=buisness,
    )
    data = {
        'message': message,
        'title': title,
        'type': noti.ntype,
        'buisness_name': buisness.name,  
        'buisness_id': buisness.id,  
        'user': buisness.user.username,
    }
    
    notify_user.delay(data) 
    return True


def enquiry_report(buisness, enquiry_details):
    """
    Function to handle enquiry report notifications.
    """
    title = "New enquiry"
    message = (
        f"A new enquiry has been received for your business. "
        f"Details: {enquiry_details}"
    )
    noti = Notification.objects.create(    
        user=buisness.user,
        message=message,
        title=title,
        ntype=Notification.NotificationType.ENQUIRY_REPORT,
        buisness=buisness,
    )
    
    data = {
        'message': message,
        'title': title,
        'type': noti.ntype,
        'buisness_name': buisness.name,  
        'buisness_id': buisness.id,  
        'user': buisness.user.username,
    }
    
    notify_user.delay(data) 
    return True


# Additional suggested notification types

def payment_reminder(buisness, days_remaining):
    """
    Function to handle payment reminder notifications.
    """
    title = "Payment reminder"
    message = (
        f"Your plan will expire in {days_remaining} days. "
        "Please renew to avoid service interruption."
    )
    noti = Notification.objects.create(    
        user=buisness.user,
        message=message,
        title=title,
        ntype=Notification.NotificationType.PAYMENT_REMINDER,
        buisness=buisness,
    )
    
    data = {
        'message': message,
        'title': title,
        'type': noti.ntype,
        'buisness_name': buisness.name,  
        'buisness_id': buisness.id,  
        'user': buisness.user.username,
    }
    
    notify_user.delay(data) 
    return True


def new_feature_announcement(buisness, feature_details):
    """
    Function to handle new feature announcements.
    """
    title = "New feature available"
    message = (
        f"A new feature is now available: {feature_details}. "
        "Check it out in your dashboard!"
    )
    
    noti = Notification.objects.create(    
        user=buisness.user,
        message=message,
        title=title,
        ntype=Notification.NotificationType.BI_UPDATES,
        buisness=buisness,
    )
    
    data = {
        'message': message,
        'title': title,
        'type': noti.ntype,
        'buisness_name': buisness.name,  
        'buisness_id': buisness.id,  
        'user': buisness.user.username,
    }
    
    notify_user.delay(data) 
    return True
 

# def support_ticket_update(buisness, ticket_id, status):
#     """
#     Function to handle support ticket updates.
#     """
#     title = "Support ticket update"
#     message = (
#         f"Your support ticket #{ticket_id} has been updated. "
#         f"Current status: {status}"
#     )
#     noti = Notification.objects.create(    
#         user=buisness.user,
#         message=message,
#         title=title,
#         ntype=Notification.NotificationType.,
#         buisness=buisness,
#     )
    
#     data = {
#         'message': message,
#         'title': title,
#         'type': 'support_ticket_update',
#         'business': business,
#         'user': business.user,
#     }
    
#     return notify_user(data) 

# def system_maintenance_notice(business, maintenance_time):
#     """
#     Function to handle system maintenance notifications.
#     """
#     title = "Scheduled maintenance"
#     message = (
#         f"The system will be undergoing maintenance on {maintenance_time}. "
#         "Please plan your activities accordingly."
#     )
    
#     data = {
#         'message': message,
#         'title': title,
#         'type': 'system_maintenance',
#         'business': business,
#         'user': business.user,
#     }
    
#     return notify_user(data) 