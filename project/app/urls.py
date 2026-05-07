from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_view),
    path('login/', views.login_view),
    path('register/', views.register_view),
    path('home/', views.home),
    path('logout/', views.logout_view),
    path('dashboard/', views.dashboard),
    path('admin-dashboard/', views.admin_dashboard),
    path('manager-dashboard/', views.manager_dashboard),

    path('add/', views.add_project),
    path('update/<int:id>/', views.update_project),
    path('delete/<int:id>/', views.delete_project),
    path('add-expense/', views.add_expense),

    # Global Production Management Routes
    path('add-actor/', views.add_actor),
    path('add-scene/', views.add_scene),
    path('add-schedule/', views.add_schedule),

    # Production Management Routes
    path('project/<int:id>/', views.project_details),
    
    path('project/<int:project_id>/add-actor/', views.add_actor),
    path('actor/delete/<int:id>/', views.delete_actor),
    
    path('project/<int:project_id>/add-scene/', views.add_scene),
    path('scene/update/<int:id>/', views.update_scene),
    path('scene/delete/<int:id>/', views.delete_scene),
    
    path('project/<int:project_id>/add-schedule/', views.add_schedule),
    path('schedule/delete/<int:id>/', views.delete_schedule),
]