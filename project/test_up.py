import os
import sys

import django.db.backends.mysql.base
django.db.backends.mysql.base.DatabaseWrapper.check_database_version_supported = lambda self: None

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'project.settings')
import django
django.setup()

from app.models import UserProfile
print(str(UserProfile.objects.all().query))
