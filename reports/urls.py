from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='reports-index'),  # Placeholder route
]