from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import Buisness_Videos
from .tasks import convert_video_to_hls

@receiver(post_save, sender=Buisness_Videos)
def handle_video_upload(sender, instance, created, **kwargs):
    if created and instance.video_file:
        print('signal triggered')
        convert_video_to_hls.delay(instance.id, instance.video_file.path)
