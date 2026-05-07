"""
WSGI config for project project.

It exposes the WSGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/6.0/howto/deployment/wsgi/
"""

import os
from django.core.wsgi import get_wsgi_application

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')

application = get_wsgi_application()

# --- Automatically create users on startup ---
try:
    from django.contrib.auth.models import User
    from app.models import UserProfile

    def create_user_with_role(username, password, role):
        if not User.objects.filter(username=username).exists():
            user = User.objects.create_user(username=username, password=password)
            # The userprofile is auto-created by signals, we just update the role
            profile = user.userprofile
            profile.role = role
            profile.save()
            print(f"Created {username} with role {role}")

    create_user_with_role('admin_user', 'admin123', 'admin')
    create_user_with_role('manager_user', 'manager123', 'production_manager')
    create_user_with_role('viewer_user', 'viewer123', 'viewer')
except Exception as e:
    print(f"Skipping user creation: {e}")
