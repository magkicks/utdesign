from django.urls import path
from . import views
from .views import faculty_dashboard, export_groups_to_csv
from .views import groups_tab
from .views import group_formation_view
from .views import assign_proposal_view, faculty_dashboard
from .views import delete_group
from .views import sponsor_view_submissions
app_name = 'accounts'

urlpatterns = [
    path('', views.landing_page, name='landing'),
    path('profile/', views.profile_view, name='profile'),
    path('register/', views.register, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('students/', views.student_dashboard, name='student-dashboard'),
    path('faculty/', views.faculty_dashboard, name='faculty-dashboard'),
    path('sponsors/', views.sponsor_dashboard, name='sponsor-dashboard'),
    path('student-dashboard/', views.student_dashboard, name='student_dashboard'),
    path('faculty-dashboard/', views.faculty_dashboard, name='faculty_dashboard'),
    path('sponsor-dashboard/', views.sponsor_dashboard, name='sponsor_dashboard'),
    path('all-proposals/', views.all_proposals, name='all_proposals'),
    path('group_formation/', views.group_formation_view, name='group_formation'),  # Use consistent name here
    path('export-groups-csv/', views.export_groups_to_csv, name='export_groups_to_csv'),
    path('faculty-dashboard/groups/', views.groups_tab, name='groups_tab'),
    path('faculty-dashboard/groups/export-csv/', views.export_groups_to_csv, name='export_groups_to_csv'),
    path('assign-proposal/<int:group_id>/', views.assign_proposal_view, name='assign_proposal'),
    path('assigned-proposals/', views.assigned_proposals_view, name='assigned_proposals'),  # For student dashboard
    path('faculty-dashboard/', views.faculty_dashboard, name='faculty_dashboard'),
    path('delete-group/<int:group_id>/', delete_group, name='delete_group'),
    path('manage-groups/', views.manage_groups, name='manage_groups'),  # Optional for a dedicated page
    path('groups-and-assigned-proposals/', views.groups_and_assigned_proposals, name='groups_and_assigned_proposals'),
    path('faculty/assign-tasks/', views.assign_tasks, name='assign_tasks'),
    path('student/tasks/', views.student_tasks, name='student_tasks'),
    path('assigned-tasks/', views.assigned_tasks, name='assigned_tasks'),
    path('faculty/view-submissions/<int:task_id>/', views.view_submissions, name='view_submissions'),
    path('sponsor/view-submissions/', views.sponsor_view_submissions, name='sponsor_view_submissions'),
    path('submit-task/<int:task_id>/', views.submit_task, name='submit_task'),
    path('sponsor/submissions/', views.sponsor_view_submissions, name='sponsor_view_submissions'),
    path('submissions/<int:task_id>/', views.view_submissions, name='view_submissions'),
    path('view-submissions/<int:task_id>/', views.view_submissions, name='view_submissions'),
]