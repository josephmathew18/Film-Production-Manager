from django.contrib import admin
from .models import Project, Actor, Scene, Schedule, Expense, UserProfile

admin.site.register(Project)
admin.site.register(Actor)
admin.site.register(Scene)
admin.site.register(Schedule)
admin.site.register(Expense)
admin.site.register(UserProfile)