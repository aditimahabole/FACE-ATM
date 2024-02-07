from os import name
from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('login/',views.login_page,name='login_page'),
    path('register/',views.register_page,name='register_page'),
    path('home/',views.home_page,name='home_page'),
    
    
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)