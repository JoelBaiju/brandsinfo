from django.db import models
from usershome.models import *

class Notification(models.Model):
    user = models.ForeignKey(Extended_User, on_delete=models.CASCADE, related_name="notifications")
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    timestamp = models.DateTimeField(auto_now_add=True)
    buisness = models.ForeignKey(Buisnesses, on_delete=models.CASCADE, related_name="notifications", null=True, blank=True)
    def __str__(self):
        return f"Notification for {self.user.username}: {self.message}"
