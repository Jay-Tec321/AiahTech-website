from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('about/', views.about, name='about'),
    path('computers/', views.computers, name='computers'),
    path('computers/<int:computer_id>/', views.computer_detail, name='computer_detail'),
    path('computers/<int:computer_id>/inquire/', views.inquire_computer, name='inquire_computer'),
    # App URLs
    path('apps/', views.apps, name='apps'),
    path('apps/<slug:slug>/', views.app_detail, name='app_detail'),
    path('apps/<slug:slug>/download/', views.download_app, name='download_app'),
]
