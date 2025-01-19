from django.urls import path
from . import views

urlpatterns = [
    path('shorten', views.shorten_url, name='shorten_url'),
    path('<str:short_url>', views.redirect_url, name='redirect_url'),
    path('analytics/<str:short_url>', views.get_analytics, name='get_analytics'),
]