from rest_framework.urls import path
from . import views

urlpatterns = [
    path('get_league/', views.get_league),
    path('bet/', views.bet),
    path('get_ranking/', views.get_ranking),

]
