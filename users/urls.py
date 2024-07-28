from rest_framework.urls import path

from . import views

urlpatterns = [
    path('login/', views.login),
    path('splash/', views.splash),
    path('get_user/', views.get_user),
]
