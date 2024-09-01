from rest_framework.urls import path
from . import views

urlpatterns = [
    path('get_league/', views.get_league),
    path('bet/', views.bet),
    path('get_ranking/', views.get_ranking),
    path('get_groups/', views.get_groups),
    path('create_group/', views.create_group),
    path('join_group/', views.join_group),
    path('leave_group/', views.leave_group),
    path('add_team/', views.add_team),
    path('add_match/', views.add_match),

]
