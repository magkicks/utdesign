# forms.py
from django import forms
from .models import Member 
from .models import Group
from proposals.models import Proposal
from django.contrib.auth.forms import UserCreationForm
from .models import UserProfile
from django.contrib.auth.models import User
from django.core.validators import RegexValidator
from django import forms
from .models import Task
from .models import Member, Group, Task, TaskSubmission 

class ProposalPreferenceField(forms.IntegerField):
    def __init__(self, proposal, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.label = proposal.title


class GroupFormationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        proposals = Proposal.objects.all()

        # Add fields for proposal preferences
        for proposal in proposals:
            self.fields[f'preference_{proposal.id}'] = forms.IntegerField(
                label=f"{proposal.title}",
                required=False,
                min_value=1,
                max_value=10,
                help_text="Rank this proposal from 1 (highest preference) to 10 (lowest preference)."
            )

        
        for i in range(1, 7):  # For 6 group members
            self.fields[f'member_name_{i}'] = forms.CharField(
                label=f"Member {i} Name", required=False
            )
            self.fields[f'member_email_{i}'] = forms.EmailField(
                label=f"Member {i} Email", required=False
            )
            self.fields[f'member_phone_{i}'] = forms.CharField(
                label=f"Member {i} Phone", required=False
            )

       
        for i in range(1, 4):  # For 3 time slots
            self.fields[f'time_slot_{i}'] = forms.CharField(
                label=f"Time Slot {i}", required=False,
                widget=forms.TextInput(attrs={'placeholder': 'e.g., Mon 2-4p'})
            )

    # Group leader as a CharField
    leader = forms.CharField(
        label="Group Leader",
        required=False,
        widget=forms.TextInput(attrs={'placeholder': 'Enter leader name'}),
        help_text="Enter the leader's name (optional)."
    )

    class Meta:
        model = Group
        fields = ['name', 'leader', 'meeting_slots', 'preferences']
        widgets = {
            'meeting_slots': forms.TextInput(attrs={'placeholder': 'Enter meeting slots'}),
        }

    def clean(self):
        cleaned_data = super().clean()

        # Validate proposal preferences
        preferences = {
            key: value for key, value in cleaned_data.items() if key.startswith('preference_')
        }
        if len(set(preferences.values())) != len(preferences.values()):
            raise forms.ValidationError("Each proposal must have a unique rank.")

        return cleaned_data

    def save(self, commit=True):
        instance = super().save(commit=False)

        # Handle meeting slots
        meeting_slots = [
            self.cleaned_data.get(f'time_slot_{i}') for i in range(1, 4)
        ]
        instance.meeting_slots = [slot for slot in meeting_slots if slot]

        if commit:
            instance.save()
        return instance
        
class CustomUserCreationForm(UserCreationForm):
    class Meta:
        model = UserProfile
        fields = ['username', 'email', 'role', 'password1', 'password2']

    # Update username field to allow spaces
    username = forms.CharField(
        max_length=150,
        required=True,
        validators=[
            RegexValidator(
                regex=r'^[\w\s]+$',  # Allows characters and spaces
                message="Username can only contain letters, numbers, and spaces."
            )
        ],
        help_text="Username can contain letters, numbers, and spaces."
    )

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'description', 'attachment', 'proposal']

class TaskSubmissionForm(forms.ModelForm):
    class Meta:
        model = TaskSubmission
        fields = ['task', 'content', 'attachment']

    def __init__(self, *args, **kwargs):
        # Allow passing a specific queryset via kwargs
        task_queryset = kwargs.pop('task_queryset', Task.objects.all())
        specific_task = kwargs.pop('task', None)  # Option to pass a single task
        super().__init__(*args, **kwargs)

        if specific_task:
            # Limit the queryset to the specific task
            self.fields['task'].queryset = Task.objects.filter(id=specific_task.id)
            self.fields['task'].initial = specific_task
            self.fields['task'].disabled = True  # Disable if a specific task is pre-selected
        else:
            # Use the provided task_queryset for general task population
            self.fields['task'].queryset = task_queryset
            self.fields['task'].label = "Select Task"


class FeedbackForm(forms.ModelForm):
    class Meta:
        model = TaskSubmission
        fields = ['faculty_comment', 'sponsor_comment']
        widgets = {
            'faculty_comment': forms.Textarea(attrs={'placeholder': 'Add faculty feedback...'}),
            'sponsor_comment': forms.Textarea(attrs={'placeholder': 'Add sponsor feedback...'}),
        }