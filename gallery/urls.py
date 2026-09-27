from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('gallery/', views.gallery_list, name='gallery_list'),
    path('gallery/<int:pk>/', views.painting_detail, name='painting_detail'),
    path('about/', views.about, name='about'),
    path('contact/', views.contact, name='contact'),
    path('set-language/', views.set_language, name='set_language'),
]
