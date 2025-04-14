from celery import shared_task
import os
import subprocess
from django.conf import settings
from .models import Buisness_Videos



@shared_task(bind=True, name="usershome.tasks.convert_video_to_hls")
def convert_video_to_hls(self, video_id, video_path):
    try:
        # Use explicit absolute path to ffmpeg
        ffmpeg_executable = r'C:\Users\91703\ffmpeg\ffmpeg-2025-03-31-git-35c091f4b7-essentials_build\bin\ffmpeg.exe'
        
        if not os.path.exists(ffmpeg_executable):
            raise Exception(f"FFmpeg not found at {ffmpeg_executable}")
        
        # Create output directory
        output_dir = os.path.join(settings.MEDIA_ROOT, 'hls', str(video_id))
        os.makedirs(output_dir, exist_ok=True)
        
        output_path = os.path.join(output_dir, 'playlist.m3u8')
        
        # FFmpeg command
        cmd = [
            ffmpeg_executable,
            '-y',  # Overwrite without asking
            '-i', video_path,
            '-c:v', 'libx264',
            '-c:a', 'aac',
            '-hls_time', '10',
            '-hls_list_size', '0',
            '-hls_segment_filename', os.path.join(output_dir, 'segment_%03d.ts'),
            '-f', 'hls',
            output_path
        ]
        
        # Run command
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            shell=True
        )
        
        if result.returncode != 0:
            raise Exception(f"FFmpeg failed: {result.stderr}")
        
        # Update model
        video = Buisness_Videos.objects.get(id=video_id)
        video.hls_path = os.path.relpath(output_path, settings.MEDIA_ROOT)
        video.is_converted = True
        video.save(update_fields=['hls_path', 'is_converted'])
        
        return f"Successfully converted video {video_id}"
        
    except Exception as e:
        self.retry(exc=e, countdown=60, max_retries=3)