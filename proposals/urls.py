from django.urls import path
from . import views

app_name = 'proposals'

urlpatterns = [
    # Example URL pattern for proposals
    path('', views.index, name='proposals-index'),
    path('submit/', views.submit_proposal, name='submit_proposal'),
    path('delete/<int:proposal_id>/', views.delete_proposal, name='delete_proposal'),
]
