from django.http import HttpResponse
from django.shortcuts import redirect

def allowed_users(allowed_roles=[]):
    def decorator(view_func):
        def wrapper_func(request, *args, **kwargs):
            if request.user.is_superuser:
                return view_func(request, *args, **kwargs)
                
            if hasattr(request.user, 'userprofile'):
                role = request.user.userprofile.role
                if role in allowed_roles or role == 'admin':
                    return view_func(request, *args, **kwargs)
                else:
                    return HttpResponse('You are not authorized to view this page or perform this action.')
            return HttpResponse('User profile not found. Contact administrator.')
        return wrapper_func
    return decorator
