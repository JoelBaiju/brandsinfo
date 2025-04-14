

from django.contrib import admin
from django.urls import path,include
from .views import *

urlpatterns = [
        path('notifyuser/', notify_user_to_all, name='notify_user'),
        path('notifications/', Notifications_View.as_view()),
]


