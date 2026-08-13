from django.shortcuts import render
from .resource_monitor import get_ram_status

def dashboard(request):
    context = {
        'ram_status': get_ram_status(),
    }
    return render(request, 'dashboard.html', context)