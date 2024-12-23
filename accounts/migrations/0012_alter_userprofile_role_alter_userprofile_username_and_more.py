# Generated by Django 5.1.4 on 2024-12-12 10:01

import django.core.validators
import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0011_alter_member_email'),
    ]

    operations = [
        migrations.AlterField(
            model_name='userprofile',
            name='role',
            field=models.CharField(choices=[('student', 'Student'), ('faculty', 'Faculty'), ('sponsor', 'Sponsor')], default='student', max_length=50),
        ),
        migrations.AlterField(
            model_name='userprofile',
            name='username',
            field=models.CharField(help_text='Required. 150 characters or fewer. Letters, numbers, and spaces only.', max_length=150, unique=True, validators=[django.core.validators.RegexValidator(message='Username can only contain letters, numbers, and spaces.', regex='^[\\w\\s]+$')]),
        ),
        migrations.CreateModel(
            name='Task',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=200)),
                ('description', models.TextField()),
                ('attachment', models.FileField(blank=True, null=True, upload_to='tasks/')),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('created_by', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='created_tasks', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
