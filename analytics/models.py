from django.db import models



from django.db import models

class RequestLog(models.Model):
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField(null=True, blank=True)
    accept_language = models.CharField(max_length=256, null=True, blank=True)
    referer = models.URLField(null=True, blank=True)
    origin = models.URLField(null=True, blank=True)
    method = models.CharField(max_length=10)
    path = models.TextField()
    query_params = models.TextField(null=True, blank=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.ip_address} - {self.path} [{self.method}]"

