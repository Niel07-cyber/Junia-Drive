# accounts/context_processors.py
from django.db.models import Sum
from .models import File

def storage_info(request):
 if request.user.is_authenticated:
    storage_limit = 100 * 1024 * 1024  # 100 MB in bytes
    space_used = File.objects.filter(folder__user=request.user).aggregate(total_size=Sum('size'))['total_size'] or 0
    space_remaining = max(storage_limit - space_used, 0)
    storage_used_percent = round((space_used / storage_limit) * 100, 2) if storage_limit > 0 else 0
    
    return {
        'storage_limit': round(storage_limit / (1024 * 1024), 2),
        'space_used': round(space_used / (1024 * 1024), 2),
        'space_remaining': round(space_remaining / (1024 * 1024), 2),
        'storage_used_percent': storage_used_percent,
    }
 else:
    return {
            'space_used': 0,
            'space_remaining': 0,
            'storage_limit': 0,
        }
