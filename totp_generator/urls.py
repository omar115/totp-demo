from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.totp_home, name='home'),
    path('generate-totp/', views.generate_totp, name='generate_totp'),
    path('generate-qr/', views.generate_qr, name='generate_qr'),
]