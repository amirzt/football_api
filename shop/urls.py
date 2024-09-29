from rest_framework.urls import path

from . import views

urlpatterns = [
    path('get_plans/', views.get_plans),
    path('get_zarinpal_url/', views.get_zarinpal_url),
    path('send_request/', views.send_request),
    path('verify/', views.verify),
    path('lottery/', views.lottery),
    path('get_chances/', views.get_chances),

    path('get_lottery_url/', views.get_lottery_url),
    path('send_lottery_request/', views.send_lottery_request),
    path('lottery_verify/', views.lottery_verify),
    path('use_chance/', views.use_chance),

    path('add_bazar_myket_membership/', views.add_bazar_myket_membership),
    path('add_bazar_myket_chance/', views.add_bazar_myket_chance),

]
