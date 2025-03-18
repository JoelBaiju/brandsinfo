from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import redirect
from django.core.exceptions import ObjectDoesNotExist

from usershome.models import Sitemap_Links
from .settings import FRONTEND_BASE_URL_FOR_SM
from django.http import HttpResponseRedirect


def mapper_view(request, maping_id):
    
    print('mapper_view')
    print(maping_id)
    try:
        link = Sitemap_Links.objects.get(id=maping_id).link
        return redirect(link)
    except ObjectDoesNotExist:
        print({"error": "Sitemap link not found."})
    except Exception as e:
        print({"error": str(e)})
    return redirect(FRONTEND_BASE_URL_FOR_SM)




