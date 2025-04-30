from celery import shared_task
import os
import subprocess
from django.conf import settings
from .models import Buisness_Videos , Buisnesses , Buisness_Offers , Plans
from django.utils import timezone
from communications.ws_notifications import plan_expired ,payment_reminder
from datetime import timedelta
from brandsinfo.settings import ffmpeg_executable

import os
import subprocess
from celery import shared_task
from django.conf import settings
from .models import Buisness_Videos  # adjust import as needed







@shared_task(bind=True, name="usershome.tasks.convert_video_to_hls")
def convert_video_to_hls(self, video_id, video_path):
    try:

        if not os.path.exists(ffmpeg_executable):
            print(f"FFmpeg not found at {ffmpeg_executable}")
            raise Exception(f"FFmpeg not found at {ffmpeg_executable}")
        
        output_dir = os.path.join(settings.MEDIA_ROOT, 'hls', str(video_id))
        os.makedirs(output_dir, exist_ok=True)
        
        output_path = os.path.join(output_dir, 'playlist.m3u8')
        
        cmd = [
            ffmpeg_executable,
            '-y',
            '-i', video_path,
            '-c:v', 'libx264',
            '-c:a', 'aac',
            '-hls_time', '10',
            '-hls_list_size', '0',
            '-hls_segment_filename', os.path.join(output_dir, 'segment_%03d.ts'),
            '-f', 'hls',
            output_path
        ]
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print('FFmpeg error:', result.stderr)
            raise Exception(f"FFmpeg failed: {result.stderr}")
        
        video = Buisness_Videos.objects.get(id=video_id)
        video.hls_path = os.path.relpath(output_path, settings.MEDIA_ROOT)
        video.is_converted = True
        video.save(update_fields=['hls_path', 'is_converted'])
        
        return f"Successfully converted video {video_id}"
    
    except Exception as e:
        print(f"Error converting video {video_id}: {e}")
        self.retry(exc=e, countdown=60, max_retries=3)








@shared_task(name='userhome.tasks.Expiry_Check')
def Expiry_Check():
    print("Running my daily task at 3 AM!")
    default_plan = Plans.objects.get(plan_name="Default Plan")
    
    expired_buisnesses = Buisnesses.objects.filter( plan_expiry_date__lt=timezone.now())

    two_days_from_now = timezone.now().date() + timedelta(days=2)
    expiring_soon_businesses = Buisnesses.objects.filter(plan_expiry_date=two_days_from_now)
    expired_offers = Buisness_Offers.objects.filter(valid_upto__lt=timezone.now())
    
    for buisness in expired_buisnesses:
        print(f"Buisness {buisness.name} has expired.")
        
        plan_expired(buisness)
        buisness.plan = default_plan
        buisness.plan_expiry_date = None
        buisness.plan_start_date = None
        buisness.plan_variant = None
        buisness.save()
    
    for buisness in expiring_soon_businesses:   
        print(f"Buisness {buisness.name} is expiring soon.")
        (buisness)
        payment_reminder(buisness , '2')        
        
    for offer in expired_offers:
        offer.is_active = False
        offer.save()    
       
       
       

    
    
    
