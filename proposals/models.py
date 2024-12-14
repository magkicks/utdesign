import os
from django.db import models
#from accounts.models import UserProfile  # Ensure this import matches your UserProfile location
# proposals/models.py
from django.contrib.auth import get_user_model

User = get_user_model()  # Dynamically retrieve the user model

class Proposal(models.Model):
    proposal_number = models.CharField(max_length=10, unique=True, editable=False)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    file = models.FileField(upload_to='proposals/')
    sponsor = models.ForeignKey(
    'accounts.UserProfile',  # Use string reference
    on_delete=models.CASCADE,
    related_name='proposals'
)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        # Generate a unique proposal number if it doesn't exist
        if not self.proposal_number:
            last_proposal = Proposal.objects.order_by('-id').first()
            next_number = 1 if not last_proposal else int(last_proposal.proposal_number.split('-')[1]) + 1
            self.proposal_number = f"PROP-{next_number:03d}"
        super().save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        # Automatically delete the file from the file system when the proposal is deleted
        if self.file and os.path.isfile(self.file.path):
            os.remove(self.file.path)
        super().delete(*args, **kwargs)

	