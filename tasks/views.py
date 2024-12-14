from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import viewsets
from .models import Task
from .serializers import TaskSerializer

# DRF ViewSet
class TaskViewSet(viewsets.ModelViewSet):
    """
    A viewset for viewing and editing Task instances.
    """
    queryset = Task.objects.all()
    serializer_class = TaskSerializer

# Basic index view for demonstration
def index(request):
    return HttpResponse("Tasks index page")
