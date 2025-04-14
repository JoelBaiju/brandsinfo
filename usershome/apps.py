from django.apps import AppConfig
from django.db.utils import OperationalError
from django.db.models import Q

class UsershomeConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "usershome"


    def ready(self):
        import usershome.signals
        from .models import Plans , Buisnesses
        try:
            if not Plans.objects.filter(plan_name='Default Plan').exists():
                plan=Plans.objects.create(plan_name="Default Plan")
                plan.save()

                buisnesses = Buisnesses.objects.filter(Q(plan=None) | Q(plan__plan_name='Default Plan'))
                
                if buisnesses.exists():
                    for business in buisnesses:
                        business.plan = plan              
                    Buisnesses.objects.bulk_update(buisnesses, ['plan'])
            else:
                print("Plans are set ready to go")
        except OperationalError:
            print("❌ Database not ready yet. Skipping startup check.")