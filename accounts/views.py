from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.forms import UserCreationForm
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from .models import UserProfile
from .forms import CustomUserCreationForm
from proposals.models import Proposal
from .forms import GroupFormationForm
from .models import Group, Member
from django.http import HttpResponse
import csv
from django.db import IntegrityError
from django.db import transaction
from django.contrib import messages
from django.urls import reverse
from django.shortcuts import render, get_object_or_404, redirect
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.db.models.signals import post_delete
from django.dispatch import receiver
from accounts.models import UserProfile
from .models import Task
from .forms import TaskForm
from .models import TaskSubmission
from .forms import TaskSubmissionForm

#Profile view
@login_required
def profile_view(request):
    return render(request, 'accounts/profile.html')

# User registration view
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)  #log in the user after registration
            messages.success(request, 'Account created successfully!')
            if user.role == 'student':
                return redirect('accounts:student_dashboard')
            elif user.role == 'faculty':
                return redirect('accounts:faculty_dashboard')
            elif user.role == 'sponsor':
                return redirect('accounts:sponsor_dashboard')
        else:
            print(form.errors)  # Debugging
            messages.error(request, 'Error creating account. Please try again.')
    else:
        form = CustomUserCreationForm()
    return render(request, 'accounts/register.html', {'form': form})

# login view
def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            # Redirect to corresponding dashboard based on the user's role
            if user.role == 'student':
                return redirect('accounts:student_dashboard')
            elif user.role == 'faculty':
                return redirect('accounts:faculty_dashboard')
            elif user.role == 'sponsor':
                return redirect('accounts:sponsor_dashboard')
            else:
                messages.error(request, 'Invalid role')
                return redirect('accounts:login')
        else:
            messages.error(request, 'Invalid username or password')
    return render(request, 'accounts/login.html')

# logout view
def logout_view(request):
    # Add logout logic
     logout(request)
     return redirect('/')

# Student dashboard view

@login_required
def dashboard_redirect(request):
    role = request.user.userprofile.role 
    if role == 'student':
        return redirect('student_dashboard')
    elif role == 'faculty':
        return redirect('faculty_dashboard')
    elif role == 'sponsor':
        return redirect('sponsor_dashboard')

@login_required
def student_dashboard(request):
    try:
        # Get the Member instance
        member = Member.objects.get(user=request.user)

        # Get the groups the student is a member of
        groups = Group.objects.filter(members=member).select_related('assigned_proposal')

        # Collect all proposals assigned to the student's groups
        proposals = [group.assigned_proposal for group in groups if group.assigned_proposal]

    except Member.DoesNotExist:
        # If user is not linked to a Member
        groups = []
        proposals = []

    return render(request, 'accounts/student_dashboard.html', {
        'groups': groups,
        'proposals': proposals,
    })

# Faculty dashboard view
@login_required
def faculty_dashboard(request):
    groups = Group.objects.prefetch_related('members').all()
    return render(request, 'accounts/faculty_dashboard.html', {"groups": groups})

# Sponsor dashboard view
@login_required
def sponsor_dashboard(request):
    user = request.user
    sponsor_proposals = Proposal.objects.filter(sponsor=user)
    groups = Group.objects.filter(assigned_proposal__sponsor=user).prefetch_related('members')

    return render(request, 'accounts/sponsor_dashboard.html', {
        'proposals': sponsor_proposals,
        'groups': groups,
    })



def landing_page(request):
    return render(request, 'accounts/landing.html')

@login_required
def all_proposals(request):
    proposals = Proposal.objects.all()
    return render(request, 'accounts/all_proposals.html', {'proposals': proposals})

def group_formation_view(request):
    proposals = Proposal.objects.all()
    member_range = range(1, 7)
    time_slots_range = range(1, 4)

    if request.method == "POST":
        form = GroupFormationForm(request.POST)
        if form.is_valid():
            try:
                print("Starting group formation process.")  # Debug

                # Save group to ensure it has an ID
                try:
                    group = form.save(commit=False)
                    group.save()  # Save the group to the database (assigns an ID)
                    print(f"Group saved: {group}")  # Debug saved group
                    print(f"Group ID before save: {group.id}")
                except Exception as save_error:
                    print(f"Error saving group: {save_error}")
                    raise save_error

                # Collect members
                members = []
                try:
                    for i in member_range:
                        member_name = form.cleaned_data.get(f'member_name_{i}')
                        member_email = form.cleaned_data.get(f'member_email_{i}')
                        member_phone = form.cleaned_data.get(f'member_phone_{i}')
                        if member_name and member_email and member_phone:
                            # Check if a user profile exists for this email
                            user_profile = UserProfile.objects.filter(email=member_email).first()

                            # If a user profile exists, check if a Member is already linked
                            if user_profile:
                                member = Member.objects.filter(user=user_profile).first()
                                if not member:
                                    member = Member.objects.create(
                                        user=user_profile,
                                        name=member_name,
                                        email=member_email,
                                        phone=member_phone
                                    )
                                    created = True
                                else:
                                    if member.phone != member_phone:
                                       member.phone = member_phone
                                       member.save()  # Save changes
                                    created = False
                            else:
                                # If no user profile, create a new member without linking to UserProfile
                                member, created = Member.objects.get_or_create(
                                    name=member_name,
                                    email=member_email,
                                    defaults={'phone': member_phone} 
                                )

                            members.append(member)
                            print(f"Processed member: {member} (Created: {created})")  # Debug
                except Exception as member_error:
                    print(f"Error processing members: {member_error}")
                    raise member_error

                # Assign members to group
                try:
                    if members:
                        group.members.add(*members)  # Use `add` instead of `set`
                        print(f"Members assigned to group {group.id}: {members}")  # Debug
                except Exception as member_assign_error:
                    print(f"Error assigning members: {member_assign_error}")
                    raise member_assign_error

                # Collect preferences
                try:
                    preference_ids = [
                        int(key.split('_')[1])
                        for key, value in form.cleaned_data.items()
                        if key.startswith('preference_') and value
                    ]
                    preferences = Proposal.objects.filter(id__in=preference_ids)
                    print(f"Collected preferences: {preferences}")  # Debug
                except Exception as preference_error:
                    print(f"Error collecting preferences: {preference_error}")
                    raise preference_error

                # Assign preferences to group
                try:
                    if preferences.exists():
                        group.preferences.add(*preferences)  # Use `add` instead of `set`
                        print(f"Preferences assigned to group {group.id}: {preferences}")  # Debug
                except Exception as preference_assign_error:
                    print(f"Error assigning preferences: {preference_assign_error}")
                    raise preference_assign_error

                messages.success(request, "Group successfully created!")
                return redirect('accounts:student_dashboard')

            except Exception as e:
                print("Error in group formation process:", e)  # error log
                messages.error(request, f"An error occurred: {e}")
        else:
            print("Form errors:", form.errors)  
            messages.error(request, "There were errors in your form submission.")
    else:
        form = GroupFormationForm()

    return render(request, 'accounts/group_formation.html', {
        'form': form,
        'proposals': proposals,
        'member_range': member_range,
        'time_slots_range': time_slots_range,
    })


def export_groups_to_csv(request):
    # Create HTTP response with CSV content type
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="groups_export.csv"'

    writer = csv.writer(response)
    writer.writerow([
        'Group Name', 'Group Leader', 'Meeting Slot 1', 'Meeting Slot 2', 'Meeting Slot 3',
        'Member Name', 'Member Email', 'Member Phone',
        '1st Choice', '2nd Choice', '3rd Choice'
    ])

    groups = Group.objects.prefetch_related('members', 'preferences').all()

    for group in groups:
        # Handle meeting slots
        slots = group.meeting_slots or ["", "", ""]
        if isinstance(slots, str):
            try:
                slots = eval(slots)  # Convert stringified list to Python list if needed
            except Exception:
                slots = ["", "", ""]  # Default to empty slots if parsing fails

        # Handle preferences
        preferences = list(group.preferences.all())
        preferences_titles = [p.title for p in preferences]
        preferences_titles += [""] * (3 - len(preferences))  # Pad with empty strings if less than 3 preferences

        # If group has no members, write a single row with blank member details
        if not group.members.exists():
            writer.writerow([
                group.name or '',
                group.leader or '',
                slots[0] if len(slots) > 0 else '',
                slots[1] if len(slots) > 1 else '',
                slots[2] if len(slots) > 2 else '',
                '',  # Blank member name
                '',  # Blank member email
                '',  # Blank member phone
                preferences_titles[0],
                preferences_titles[1],
                preferences_titles[2],
            ])
        else:
            # Collect data for each member
            for member in group.members.all():
                writer.writerow([
                    group.name or '',
                    group.leader or '',
                    slots[0] if len(slots) > 0 else '',
                    slots[1] if len(slots) > 1 else '',
                    slots[2] if len(slots) > 2 else '',
                    member.name or '',
                    member.email or '',
                    member.phone or '',
                    preferences_titles[0],
                    preferences_titles[1],
                    preferences_titles[2],
                ])

    return response

@receiver(post_delete, sender=Group)
def update_csv_on_delete(sender, instance, **kwargs):
    # Path to your CSV file
    csv_file_path = "path_to_your_csv_file.csv"  # Replace with your actual path

    try:
        # Read current data from the CSV
        with open(csv_file_path, "r") as file:
            rows = list(csv.reader(file))

        # Extract header and filter out rows related to the deleted group
        header = rows[0]
        updated_rows = [row for row in rows if row[0] != instance.name]

        # Write the updated data back to the CSV
        with open(csv_file_path, "w", newline="") as file:
            writer = csv.writer(file)
            writer.writerow(header)
            writer.writerows(updated_rows)

    except Exception as e:
        print(f"Error updating CSV on delete: {e}")
def error_view(request):
    return render(request, 'accounts/error.html')  # Assuming you have a template for errors

def groups_tab(request):
    groups = Group.objects.all()  # Get all groups
    return render(request, 'accounts/groups_tab.html', {'groups': groups})

@login_required
def assign_proposal_view(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    proposals = Proposal.objects.all()

    if request.method == "POST":
        proposal_id = request.POST.get('proposal')
        if proposal_id:
            proposal = get_object_or_404(Proposal, id=proposal_id)
            group.assigned_proposal = proposal
            group.save()
            messages.success(request, f"Proposal '{proposal.title}' assigned to group '{group.name}'.")
            return redirect('accounts:faculty_dashboard')
        else:
            messages.error(request, "Please select a proposal.")

    # Update the path to point to your template location
    return render(request, 'accounts/assign_proposal.html', {
        'group': group,
        'proposals': proposals,
    })
        
@login_required
def assigned_proposals_view(request):
    try:
        # Fetch the Member instance for the logged-in user
        member = Member.objects.get(user=request.user)

        # Retrieve groups where the logged-in user is a member
        groups = Group.objects.filter(members=member).select_related('assigned_proposal')
        print(f"Groups for user {request.user.username}: {groups}")
    except Member.DoesNotExist:
        # If the user is not linked to a Member, handle gracefully
        groups = Group.objects.none()
        print(f"No Member linked for user {request.user.username}")

    return render(request, 'accounts/assigned_proposals.html', {'groups': groups})

@csrf_exempt
def delete_group(request, group_id):
    if request.method == "POST":
        try:
            group = get_object_or_404(Group, id=group_id)
            group.delete()  # Delete the group
            return JsonResponse({"status": "success", "message": "Group deleted successfully."})
        except Exception as e:
            return JsonResponse({"status": "error", "message": str(e)})
    return JsonResponse({"status": "error", "message": "Invalid request method."})

def manage_groups(request):
    groups = Group.objects.all()
    return render(request, 'accounts/manage_groups.html', {'groups': groups})

def groups_and_assigned_proposals(request):
    groups = Group.objects.all()
    return render(request, 'accounts/groups_and_assigned_proposals.html', {'groups': groups})

@login_required
def assign_tasks(request):
    if request.user.role != 'faculty':
        messages.error(request, "You are not authorized to assign tasks.")
        return redirect('accounts:dashboard')

    tasks = Task.objects.all()  # Initialize tasks to prevent UnboundLocalError

    if request.method == 'POST':
        form = TaskForm(request.POST, request.FILES)
        proposal_id = request.POST.get('proposal_id', None)

        if form.is_valid():
            task = form.save(commit=False)
            if proposal_id:
                proposal = Proposal.objects.filter(id=proposal_id).first()
                if proposal:
                    task.proposal = proposal
            task.save()
            messages.success(request, 'Task created successfully!')
            return redirect('accounts:assign_tasks')
        else:
            messages.error(request, 'Failed to create task. Check the form for errors.')

    proposals = Proposal.objects.all()

    return render(request, 'accounts/assign_tasks.html', {
        'form': TaskForm(),
        'tasks': tasks,
        'proposals': proposals,
    })




@login_required
def student_tasks(request):
    general_tasks = Task.objects.filter(proposal__isnull=True)
    print(f"DEBUG: General tasks: {[task.title for task in general_tasks]}")

    member = Member.objects.filter(user=request.user).first()
    if member:
        groups = Group.objects.filter(members=member)
        print(f"DEBUG: Groups for member {member.name}: {[group.name for group in groups]}")

        group_tasks = Task.objects.filter(proposal__assigned_group__in=groups)
        print(f"DEBUG: Group-specific tasks: {[task.title for task in group_tasks]}")
    else:
        group_tasks = Task.objects.none()
        print("DEBUG: No member found for the logged-in user.")

    tasks = general_tasks | group_tasks
    print(f"DEBUG: Combined tasks for user {request.user.username}: {[task.title for task in tasks]}")

    return render(request, 'accounts/student_tasks.html', {'tasks': tasks})


@login_required
def assigned_tasks(request):
    try:
        # Get the current user's Member instance
        member = Member.objects.get(user=request.user)

        # Find all groups the user belongs to
        user_groups = Group.objects.filter(members=member)

        # Retrieve tasks linked to proposals assigned to the user's groups
        tasks = Task.objects.filter(proposal__assigned_group__in=user_groups).distinct()

        # Fetch submissions related to these tasks
        task_submissions = TaskSubmission.objects.filter(student=request.user, task__in=tasks).select_related('task')
    except Member.DoesNotExist:
        # Handle case where the user is not linked to any Member
        tasks = Task.objects.none()
        task_submissions = TaskSubmission.objects.none()

    return render(request, 'accounts/assigned_tasks.html', {
        'tasks': tasks,
        'task_submissions': task_submissions,  # Include task submissions
    })





@login_required
def sponsor_view_submissions(request):
    if request.user.role != 'sponsor':
        messages.error(request, "You are not authorized to view this page.")
        return redirect('accounts:dashboard')

    # Fetch proposals submitted by the sponsor
    sponsor_proposals = Proposal.objects.filter(sponsor=request.user)

    # Fetch groups assigned to these proposals
    groups = Group.objects.filter(assigned_proposal__in=sponsor_proposals).prefetch_related('members')

    # Collect user IDs of all members in those groups
    member_user_ids = [member.user_id for group in groups for member in group.members.all()]

    # Filter submissions where the submitter's user_id matches one of these user IDs
    submissions = TaskSubmission.objects.filter(student__id__in=member_user_ids).select_related('task', 'student')

    # Handle saving feedback
    if request.method == 'POST':
        sponsor_comment = request.POST.get('sponsor_comment', '').strip()
        submission_id = request.POST.get('submission_id')

        # Debugging output
        print(f"DEBUG: Sponsor Comment: {sponsor_comment}")
        print(f"DEBUG: Submission ID: {submission_id}")

        if submission_id:
            try:
                submission = get_object_or_404(TaskSubmission, id=submission_id)
                if request.user.role == 'sponsor':
                    submission.sponsor_comment = sponsor_comment
                    submission.save()
                    print("DEBUG: Sponsor comment saved successfully.")  # Debug
                    messages.success(request, 'Feedback has been saved.')
                else:
                    messages.error(request, "You are not authorized to leave feedback.")
            except Exception as e:
                print(f"DEBUG: Error saving sponsor comment: {e}")
                messages.error(request, "Failed to save feedback.")
        else:
            messages.error(request, "Submission ID is missing.")

    return render(request, 'accounts/sponsor_view_submissions.html', {
        'submissions': submissions,
    })








@login_required
def provide_feedback(request, submission_id):
    submission = get_object_or_404(TaskSubmission, id=submission_id)

    if request.user.groups.filter(name='Sponsors').exists():
        if submission.task.proposal.sponsor != request.user:
            return HttpResponseForbidden("You are not authorized to comment on this submission.")
    
    if request.method == 'POST':
        form = FeedbackForm(request.POST, instance=submission)
        if form.is_valid():
            submission = form.save(commit=False)
            if request.user.groups.filter(name='Faculty').exists():
                submission.faculty_comment = form.cleaned_data['faculty_comment']
            if request.user.groups.filter(name='Sponsors').exists():
                submission.sponsor_comment = form.cleaned_data['sponsor_comment']
            submission.save()
            return redirect('accounts:view_submissions', task_id=submission.task.id)

    form = FeedbackForm(instance=submission)
    return render(request, 'accounts/provide_feedback.html', {'form': form, 'submission': submission})

@login_required
def view_submissions(request, task_id=None):
    if request.user.role not in ['faculty', 'sponsor']:
        messages.error(request, "You are not authorized to view this page.")
        return redirect('accounts:dashboard')

    # Fetch submissions based on user role
    if request.user.role == 'faculty':
        if task_id:
            task = get_object_or_404(Task, id=task_id)
            submissions = TaskSubmission.objects.filter(task=task).select_related('task', 'student')
            title = f"Submissions for {task.title}"
        else:
            submissions = TaskSubmission.objects.all().select_related('task', 'student')
            title = "All Task Submissions"

    elif request.user.role == 'sponsor':
        sponsor_proposals = Proposal.objects.filter(sponsor=request.user)
        tasks = Task.objects.filter(proposal__in=sponsor_proposals)
        submissions = TaskSubmission.objects.filter(task__in=tasks).select_related('task', 'student')
        title = "Submissions for Your Proposals"

    else:
        submissions = []
        title = "Submissions"

    # Handle POST request for saving feedback
    if request.method == 'POST':
        sponsor_comment = request.POST.get('sponsor_comment', '').strip()
        faculty_comment = request.POST.get('faculty_comment', '').strip()
        submission_id = request.POST.get('submission_id')

        # Debugging output
        print(f"Sponsor Comment: {sponsor_comment}")
        print(f"Faculty Comment: {faculty_comment}")
        print(f"Submission ID: {submission_id}")

        if submission_id:
            try:
                submission = get_object_or_404(TaskSubmission, id=submission_id)
                if request.user.role == 'faculty':
                    submission.faculty_comment = faculty_comment
                elif request.user.role == 'sponsor':
                    submission.sponsor_comment = sponsor_comment
                else:
                    messages.error(request, "You are not authorized to leave feedback.")
                    return redirect('accounts:view_submissions')
                submission.save()
                messages.success(request, 'Feedback has been saved.')
            except Exception as e:
                print(f"Error saving comment: {e}")
                messages.error(request, "Failed to save feedback.")
        else:
            messages.error(request, "Submission ID is missing.")

    return render(request, 'accounts/view_submissions.html', {
        'submissions': submissions,
        'title': title,
    })



    # Save sponsor feedback
    if request.method == 'POST':
        sponsor_comment = request.POST.get('sponsor_comment', '')
        submission_id = request.POST.get('submission_id')
        print(f"Sponsor Comment: {sponsor_comment}")  # Debug
        print(f"Submission ID: {submission_id}")  # Debug
        submission = get_object_or_404(TaskSubmission, id=submission_id)
    if request.user.role == 'sponsor':
        submission.sponsor_comment = sponsor_comment
        submission.save()
        print("Sponsor comment saved successfully.")  # Debug
        messages.success(request, 'Feedback has been saved.')

    return render(request, 'accounts/view_submissions.html', {
        'submissions': submissions,
        'title': title,
    })


@login_required
def submit_task(request, task_id):
    # Get the specific task from the URL
    task = get_object_or_404(Task, id=task_id)

    if request.method == 'POST':
        form = TaskSubmissionForm(request.POST, request.FILES)
        if form.is_valid():
            submission = form.save(commit=False)
            submission.task = task  # Automatically associate the task
            submission.student = request.user
            submission.save()
            messages.success(request, f'Submission for task "{task.title}" saved successfully!')
            return redirect('accounts:assigned_tasks')
    else:
        form = TaskSubmissionForm()

    return render(request, 'accounts/submit_task.html', {'form': form, 'task': task})


@login_required
def delete_comments(request, submission_id):
    submission = get_object_or_404(TaskSubmission, id=submission_id)
    if request.user.role != 'faculty':  # Ensure only faculty can delete
        messages.error(request, "You are not authorized to delete comments.")
        return redirect('accounts:view_submissions')

    if request.method == 'POST':
        submission.faculty_comment = None
        submission.sponsor_comment = None
        submission.save()
        messages.success(request, "Comments deleted successfully.")
    return redirect('accounts:view_submissions', task_id=submission.task.id if submission.task else 0)

# views.py
@login_required
def update_group_progress(request, group_id):
    group = get_object_or_404(Group, id=group_id)
    if request.method == 'POST':
        new_progress = int(request.POST.get('progress', group.progress))
        group.progress = max(0, min(new_progress, 100))  # Ensure progress stays between 0–100
        group.save()
        messages.success(request, f"Progress for group '{group.name}' updated to {group.progress}%.")
        return redirect('accounts:faculty_dashboard')
    return render(request, 'accounts/update_progress.html', {'group': group})
