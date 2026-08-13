from django.shortcuts import render
from django.http import JsonResponse

def projects_list(request):
    # Return empty list for now (we'll implement later)
    return JsonResponse([], safe=False)
# Create your views here.
