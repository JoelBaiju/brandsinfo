from django.utils import timezone
import pytz
from django.forms.models import model_to_dict
import datetime
from ..models import *
from ..serializers import *
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.core.mail import EmailMultiAlternatives
from django.db.models import F, Count
from dateutil.relativedelta import relativedelta


def localtime():    
    now = timezone.now().time()
    now = timezone.now()
    local_tz = pytz.timezone('Asia/Kolkata')
    local_time = now.astimezone(local_tz)
    return local_time.time()

    
    
    
    

def count_filled_fields(instance):
    data_dict = model_to_dict(instance, exclude=["id","score"," no_of_views" , "no_of_enquiries" ,"sa_rate","user","latittude"]) 
    filled_fields = {key: value for key, value in data_dict.items() if value not in [None, "", [], {}]}
    print(filled_fields)
    return len(filled_fields)




def buisness_visits_analyzer(buisness , formatt):
    if formatt =='month':
        return total_visits_last_7_months(buisness)
    elif formatt =='week':
        return total_visits_last_7_weeks(buisness)
    else:
        return total_visits_last_7_days(buisness)

    


def total_visits_last_7_days(buisness):
    today = timezone.now().date()
    seven_days_ago = today - datetime.timedelta(days=7)
    
    visits = BuisnessVisitTracker.objects.filter(
        buisness=buisness,
        date__range=[seven_days_ago, today]
    ).values('date').annotate(count=Count('date')).order_by('date')
    
    return visits





def total_visits_last_7_weeks(buisness):
    today = timezone.now().date()
    review_data = []

    for i in range(7):  # Iterate through the last 7 weeks
        end_date = today - datetime.timedelta(days=i * 7)
        start_date = end_date - datetime.timedelta(days=6)  # 7 days in a week

        review_count = BuisnessVisitTracker.objects.filter(
            buisness=buisness,
            date__range=[start_date, end_date]
        ).count()

        review_data.append({
            'start_date': start_date.strftime('%Y-%m-%d'),
            'end_date': end_date.strftime('%Y-%m-%d'),
            'count': review_count
        })

    return review_data




import calendar

def total_visits_last_7_months(buisness):
    today = timezone.now().date()
    visit_data = []

    for i in range(7):  # Iterate through the last 7 months
        end_date = today - relativedelta(months=i)
        start_date = today - relativedelta(months=i+1)
        start_date = start_date + relativedelta(days=1)

        visit_count = BuisnessVisitTracker.objects.filter(
            buisness=buisness,
            date__range=[start_date, end_date]
        ).count()

        # Get the month name from the end_date
        month_name = calendar.month_name[end_date.month]

        visit_data.append({
            'month': month_name,  # Use month name instead of start/end dates
            'count': visit_count
        })

    return visit_data




def BuisnessScore(buisness):
    fieldcount=count_filled_fields(buisness)
    score_in_percentage=(fieldcount/21)*100
    print(score_in_percentage)
    if score_in_percentage>100:
        return 100
    return (int(score_in_percentage))

def BuisnessDcats(buisness):
    dcat = Buisness_Descriptive_cats.objects.filter(buisness=buisness)
    dcat = [i.dcat.cat_name  for i in dcat  ]
    return dcat


def number_of_enquiries(buisness):
    number = Enquiries.objects.filter(buisness=buisness).count()
    return number


def Most_searched_products_in_buisness(buisness):
    products = Products.objects.filter(buisness=buisness , searched__gte=1).order_by('-searched')[:10]
    return ProductSerializerMini(products , many=True).data


def Most_searched_services_in_buisness(buisness):
    services = Services.objects.filter(buisness=buisness , searched__gte=1).order_by('-searched')[:10]
    return ServiceSerializer(services , many=True).data






def update_search_count_products(products):
    print('search count update started')
    product_ids = list(products.values_list('id', flat=True))  # Convert queryset to a list
    Products.objects.filter(id__in=product_ids).update(searched=F('searched') + 1)
    print('search count updated')


def update_search_count_services(services):
    print('search count update started')
    services_ids = list(services.values_list('id', flat=True))  # Convert queryset to a list
    Services.objects.filter(id__in=services_ids).update(searched=F('searched') + 1)
    print('search count updated')


def update_search_count_buisnesses(buisnesses):
    print('search count update started')
    try:
        buisnesses.update(searched=F('searched') + 1)
        print(buisnesses)
    except Exception as e:
        print(e)
    print('search count updated')





def send_otp_email(firstname,otp,toemail):
    subject = 'Your OTP for Email Verification'
    html_message = render_to_string('email_otp.html', {
    'name': firstname,
    'otp': otp
    })
    plain_message = strip_tags(html_message)

    email = EmailMultiAlternatives(
    subject,
    plain_message,
    'brandsinfoguide@gmail.com',  # Replace with your "from" email address
    [toemail]    
    )
    email.attach_alternative(html_message, 'text/html')
    email.send()
    
    
    


def send_review_notification_email(
    business_name,
    business_description,
    review_type,
    rating,
    review,
    eg_review=None
):
    subject = f'📝 New Review Generated for {business_name}'

    html_message = render_to_string('review_generated_admin.html', {
        'business_name': business_name,
        'business_description': business_description,
        'review_type': review_type,
        'rating': rating,
        'review': review,
        'eg_review': eg_review
    })

    plain_message = strip_tags(html_message)

    email = EmailMultiAlternatives(
        subject,
        plain_message,
        'brandsinfoguide@gmail.com',  # Replace with your sender email
        ['brandsinfo.test@gmail.com']
    )
    email.attach_alternative(html_message, 'text/html')
    email.send()

        

    
    
    
def average_time_spent(buisness):
    return 34

def buisness_keywords(buisness):
    Keywords = Buisness_keywords.objects.filter(buisness=buisness).values_list('keyword__keyword', flat=True)
    return Keywords
    
def add_analytics(buisness , visit_format):
    buisness = Buisnesses.objects.get(id=buisness.id)

    analytics = {
        'average_time_spend': False,
        'keywords': False,
        'leads': '56',
        'most_serched_services': [],
        'most_serched_products': [],
        'searched': buisness.searched,
        'visits': False
    }

    if buisness.plan.plan_name != 'Default Plan':
        if buisness.plan.profile_visit:
            analytics['visits'] = buisness_visits_analyzer(buisness=buisness, formatt=visit_format)

        if buisness.plan.average_time_spend:
            analytics['average_time_spend'] = average_time_spent(buisness)

        if buisness.plan.keywords:
            analytics['keywords'] = buisness_keywords(buisness)

        if buisness.plan.most_searhed_p_s:
            if buisness.buisness_type == 'service':
                analytics['most_serched_services'] = Most_searched_services_in_buisness(buisness)

            elif buisness.buisness_type == 'product':
                analytics['most_serched_products'] = Most_searched_products_in_buisness(buisness)

            else:
                analytics['most_serched_services'] = Most_searched_services_in_buisness(buisness)
                analytics['most_serched_products'] = Most_searched_products_in_buisness(buisness)

    return analytics  # ✅ Always defined
