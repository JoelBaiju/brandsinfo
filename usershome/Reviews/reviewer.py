

from celery import shared_task
from celery import shared_task
from django.utils import timezone
from communications.ws_notifications import plan_expired ,payment_reminder
from datetime import timedelta
from brandsinfo.settings import ffmpeg_executable
import random



from brandsinfo.settings import AUTO_REVIEW
from..models import BusinessReviewTracker
from ..Ai.review_generator import prime_review_generator

@shared_task(bind=True, name="usershome.Reviews.reviewer.check_and_schedule_reviews")
def check_and_schedule_reviews():

    print("auto review scheduler task called")

    if not AUTO_REVIEW:
        return
    today = timezone.now().date()
    trackers = BusinessReviewTracker.objects.select_related('business')

    for tracker in trackers:
        biz = tracker.business
        plan = biz.plan
        now = timezone.now()

        # Define plan thresholds
        max_reviews_per_14_days = {
            'tier_1': random.randint(4, 5),
            'tier_2': random.randint(5, 10),
            'tier_3': random.randint(10, 15),
        }.get(plan, 0)

        # Reset cycle if needed
        if (today - tracker.cycle_start_date).days >= 14:
            tracker.reviews_added_this_cycle = 0
            tracker.cycle_start_date = today

        if tracker.reviews_added_this_cycle >= max_reviews_per_14_days:
            continue

        # If today's the day to add review(s)
        if tracker.next_review_date is None or today >= tracker.next_review_date:
            count = random.randint(1, 3)  # how many reviews to generate today

            for _ in range(count):
                delay = random.randint(0, 86400)  # seconds in 24 hrs
                add_single_review.apply_async(args=[biz.id], countdown=delay)

            # Update tracker
            tracker.reviews_added_this_cycle += count
            tracker.next_review_date = today + timedelta(days=random.randint(1, 4))
            tracker.save()











@shared_task
def add_single_review(biz_id):
    from ..models import Buisnesses, Reviews_Ratings
    from django.utils import timezone
    import random
    from ..Tools_Utils.utils import send_review_notification_email

    def weighted_rating(tier):
        if tier == 'tier_3':
            return random.choices([2, 3, 4, 5], weights=[10, 50, 30, 10])[0]  # avg ~3.5
        elif tier == 'tier_2':
            return random.choices([3, 4, 5], weights=[20, 50, 30])[0]         # avg ~4
        elif tier == 'tier_1':
            return random.choices([4, 5], weights=[40, 60])[0]               # avg ~4.5
        return 4

    def should_include_text(tier):
        chances = {
            "tier_1": 0.4,
            "tier_2": 0.5,
            "tier_3": 0.6,
        }
        return random.random() < chances.get(tier, 0.5)

    # Get business
    biz = Buisnesses.objects.get(id=biz_id)
    plan = biz.plan.plan_name

    # Generate rating
    rating = weighted_rating(plan)
    include_text = should_include_text(plan)

    # Generate review text if needed
    review_text = ""

    r_type = ''
    if rating<3:
        r_type = "bad"
    if rating>3 and rating <4:
        r_type = "medium"
    if rating>4:
        r_type = 'good'


    if include_text:
        review = prime_review_generator(biz.id,r_type , plan )


    # Select a user or fake user
    from .review_name_picker import get_random_name
    user_name = user_name = get_random_name(biz.target_audience_gender)


    now = timezone.now()

    # Save review
    Reviews_Ratings.objects.create(
        buisness=biz,
        user=None,
        user_name=user_name,
        review=review,
        rating=rating,
        date=now.date(),
        time=now.time()
    )

    # Update business avg rating and review count
    total_reviews = biz.total_no_of_ratings + 1
    total_rating_sum = biz.rating * biz.total_no_of_ratings + rating
    new_avg = round(total_rating_sum / total_reviews, 2)

    biz.rating = new_avg
    biz.total_no_of_ratings = total_reviews
    biz.save()

    send_review_notification_email(
        business_name=biz.name,
        business_description = biz.description,
        review_type = r_type,
        rating = rating,
        review = review
    )
