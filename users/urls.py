from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login_user, name='login'),
    path('send-otp/', views.send_otp, name='send_otp'),
    path('logout/', views.logout_user, name='logout'),
    path('check-user/', views.check_user, name='check_user'),
]