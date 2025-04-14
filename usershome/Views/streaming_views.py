# views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework import status
import os
from django.conf import settings
from ..models import Buisness_Videos , Buisnesses



class VideoUploadView(APIView):
    parser_classes = (MultiPartParser, FormParser)

    def post(self, request, *args, **kwargs):
        video_file = request.FILES.get('video')
        if not video_file:
            return Response({"error": "No video uploaded"}, status=status.HTTP_400_BAD_REQUEST)

        vidobj = Buisness_Videos.objects.create(
            buisness =Buisnesses.objects.get(id=request.data.get('buisness')),
            video_file=video_file,
        )
        # Save the video
        # with open(video_path, 'wb+') as destination:
        #     for chunk in video_file.chunks():
        #         destination.write(chunk)

        return Response({"message": "Video uploaded", "path": 'video_path'}, status=status.HTTP_201_CREATED)
