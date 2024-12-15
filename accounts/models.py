from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.validators import RegexValidator


# UserProfile Model
class UserProfile(AbstractUser):
    ROLE_CHOICES = (
        ('student', 'Student'),
        ('faculty', 'Faculty'),
        ('sponsor', 'Sponsor'),
    )
    role = models.CharField(max_length=50, choices=ROLE_CHOICES, default='student')

    username = models.CharField(
        max_length=150,
        unique=True,
        validators=[
            RegexValidator(
                regex=r'^[\w\s]+$',  # Allows letters, numbers, and spaces
                message="Username can only contain letters, numbers, and spaces."
            )
        ],
        help_text="Required. 150 characters or fewer. Letters, numbers, and spaces only."
    )

    def __str__(self):
        return self.username


# Member Model (Separate from UserProfile)
class Member(models.Model):
    user = models.OneToOneField('accounts.UserProfile', on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=15, blank=True, default='')

    def __str__(self):
        return self.name or "Unnamed Member"



@receiver(post_save, sender=UserProfile)
def create_member_for_user(sender, instance, created, **kwargs):
    if created and instance.role == 'student':  # Only for students
        member, created = Member.objects.get_or_create(
            user=instance,  # Link to the UserProfile
            defaults={
                'name': instance.username,
                'email': instance.email,
                'phone': ''  # Add logic for phone if needed
            }
        )
        if not created:
            print(f"Member {member} already exists and was reused.")
        else:
            print(f"New member created for user {instance.username}.")


@receiver(post_save, sender=UserProfile)
def save_member_for_user(sender, instance, **kwargs):
    if hasattr(instance, 'member'):
        instance.member.save()


# Group Model
class Group(models.Model):
    name = models.CharField(max_length=255, blank=False, null=False)  # Name is required
    leader = models.CharField(max_length=255, blank=True, null=True)
    members = models.ManyToManyField('accounts.Member', related_name='member_groups', blank=True)
    preferences = models.ManyToManyField('proposals.Proposal', related_name='preferred_groups', blank=True)
    assigned_proposal = models.ForeignKey(
        'proposals.Proposal', on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_group'
    )
    meeting_slots = models.JSONField(blank=True, null=True)
    member_details = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.name:
            raise ValueError("The 'name' field cannot be empty.")
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name or "Unnamed Group"


# Task Model
class Task(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    attachment = models.FileField(upload_to='tasks/', null=True, blank=True)
    proposal = models.ForeignKey(
        'proposals.Proposal', on_delete=models.CASCADE, null=True, blank=True, related_name='tasks'
    )



class TaskSubmission(models.Model):
    task = models.ForeignKey(Task, on_delete=models.CASCADE, related_name='submissions')
    student = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='submissions')
    content = models.TextField()
    attachment = models.FileField(upload_to='submissions/', null=True, blank=True)
    submitted_at = models.DateTimeField(auto_now_add=True)
    faculty_comment = models.TextField(null=True, blank=True)
    sponsor_comment = models.TextField(null=True, blank=True)

    def __str__(self):
        return f"{self.student.username} - {self.task.title}"

