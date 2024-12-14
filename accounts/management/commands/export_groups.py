import csv
from django.core.management.base import BaseCommand
from accounts.models import Group

class Command(BaseCommand):
    help = "Export groups to a CSV file"

    def handle(self, *args, **kwargs):
        groups = Group.objects.all()  # Fetch all groups
        with open('output.csv', 'w', newline='') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow(['Group Name', 'Leader Name', 'Meeting Slots', 'Member Details'])  # Header row
            for group in groups:
                writer.writerow([group.name, group.leader, group.meeting_slots, group.member_details])
        self.stdout.write(self.style.SUCCESS('Successfully exported groups to output.csv'))

