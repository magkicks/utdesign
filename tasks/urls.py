from django.urls import path
from . import views

urlpatterns = [
    # Placeholder route for testing
    path('', views.index, name='tasks-index'),
]
