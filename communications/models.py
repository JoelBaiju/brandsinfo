from django.db import models
from usershome.models import *

class Notification(models.Model):
    class NotificationType(models.TextChoices):
        PLAN_PURCHASED          = 'NEW_PLAN_PURCHASED', 'New Plan Purchased'
        PLAN_PURCHASE_FAILED    = 'PLAN_PURCHASE_FAILED', 'Plan Purchase Failed'
        AMOUNT_REFUNDED         = 'AMOUNT_REFUNDED', 'Amount Refunded'
        PLAN_EXPIRED            = 'PLAN_EXPIRED', 'Plan Expired'
        BI_UPDATES              = 'BI_UPDATES', 'Business Updates'
        BI_VERIFIED             = 'BI_VERIFIED', 'Business Verified'
        VISIT_REPORT            = 'VISIT_REPORT', 'Visit Report'
        ENQUIRY_REPORT          = 'ENQUIRY_REPORT', 'Enquiry Report'
        BUISNESS_UPDATES        =  'BUISNESS_UPDATES', 'Buisness Updates'
        PAYMENT_REMINDER        = 'PAYMENT_REMINDER', 'Payment Reminder'
        PAYMENT_STATUS          = 'PAYMENT_STATUS', 'Payment Status'

    user        = models.ForeignKey(Extended_User, on_delete=models.CASCADE, related_name="notifications")
    title       = models.CharField(max_length=255, null=True, blank=True)
    message     = models.TextField()    
    is_read     = models.BooleanField(default=False)
    timestamp   = models.DateTimeField(auto_now_add=True)
    buisness    = models.ForeignKey(Buisnesses, on_delete=models.CASCADE, related_name="notifications", null=True, blank=True)
    ntype       = models.CharField(max_length=50, choices=NotificationType.choices, default=NotificationType.BI_UPDATES)  
    def __str__(self):
        return f"Notification for {self.user.username}: {self.message}"
