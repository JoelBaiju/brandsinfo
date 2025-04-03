from rest_framework.permissions import BasePermission
from usershome.models import Buisnesses

class PlanFeaturePermission(BasePermission):
  

    def __init__(self, required_feature):
        self.required_feature = required_feature

    def has_permission(self, request, feature):
        bid = request.GET.get('bid')
        if not bid:
            return False
        if not request.user.is_authenticated:
            return False  
        try:
            buisness = Buisnesses.objects.get(id=bid)
            if buisness.plan[feature]==False:
                return False
            
        except Buisnesses.DoesNotExist:
            return False 

        return False  
