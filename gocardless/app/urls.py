from os import name
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('login/',views.login_page,name='login_page'),
    path('register/',views.register_page,name='register_page'),
    path('home/',views.home_page,name='home_page'),
    path('match_person/', views.match_person, name='match_person'),
    path('otp/',views.otp,name='otp'),
    path('send_email_otp/', views.send_email_otp, name='send_email_otp'),
    path('send_sms_otp/', views.send_sms_otp, name='send_sms_otp'),
    path('verify_otp/', views.verify_otp, name='verify_otp'),
    path('transaction/', views.transaction, name='transaction'),
    path('logout/', views.logout, name='logout'),
    
    
    
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)