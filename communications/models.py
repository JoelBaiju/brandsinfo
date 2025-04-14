from django.db import models
from usershome.models import *

class Notification(models.Model):
    class TransactionStatus(models.TextChoices):
        PLAN_PURCHASED          = 'NEW_PLAN_PURCHASED', 'New Plan Purchased'
        PLAN_PURCHASE_FAILED    = 'PLAN_PURCHASE_FAILED', 'Plan Purchase Failed'
        AMOUNT_REFUNDED         = 'AMOUNT_REFUNDED', 'Amount Refunded'
        PLAN_EXPIRED            = 'PLAN_EXPIRED', 'Plan Expired'
        PLAN_RENEWED            = 'PLAN_RENEWED', 'Plan Renewed'
        BI_UPDATES              = 'BI_UPDATES', 'Business Updates'
        BI_VERIFIED             = 'BI_VERIFIED', 'Business Verified'
        VISIT_REPORT            = 'VISIT_REPORT', 'Visit Report'
        ENQUIRY_REPORT          = 'ENQUIRY_REPORT', 'Enquiry Report'
        

    user        = models.ForeignKey(Extended_User, on_delete=models.CASCADE, related_name="notifications")
    title       = models.CharField(max_length=255, null=True, blank=True)
    message     = models.TextField()    
    is_read     = models.BooleanField(default=False)
    timestamp   = models.DateTimeField(auto_now_add=True)
    buisness    = models.ForeignKey(Buisnesses, on_delete=models.CASCADE, related_name="notifications", null=True, blank=True)
    ntype       = models.CharField(max_length=255, null=True, blank=True)  
    def __str__(self):
        return f"Notification for {self.user.username}: {self.message}"
