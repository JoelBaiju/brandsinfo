# tasks.py
from celery import shared_task
from django.utils.timezone import now, timedelta
from .models import Count_Per_Day
from usershome.models import Buisnesses, Products, Services, Extended_User

@shared_task(name='analysis.tasks.record_daily_count')
def record_daily_counts():
    # Get total counts up to now
    total_buisness = Buisnesses.objects.count()
    total_products = Products.objects.count()
    total_services = Services.objects.count()
    total_users = Extended_User.objects.count()

    # Get yesterday's record
    yesterday = now().date() - timedelta(days=1)
    yesterday_record = Count_Per_Day.objects.filter(timestamp__date=yesterday).last()

    if yesterday_record:
        new_buisness = total_buisness - yesterday_record.buisness
        new_products = total_products - yesterday_record.products
        new_services = total_services - yesterday_record.services
        new_users = total_users - yesterday_record.users
    else:
        new_buisness = total_buisness
        new_products = total_products
        new_services = total_services
        new_users = total_users

    Count_Per_Day.objects.create(
        buisness=new_buisness,
        products=new_products,
        services=new_services,
        users=new_users
    )
