from django.apps import AppConfig
from django.db.models.signals import post_migrate

class AccountsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'accounts'

    def modify_username_field(self, **kwargs):
        from django.contrib.auth.models import User
        from django.core.validators import RegexValidator

      
        username_field = User._meta.get_field('username')
        username_field.validators = [
            RegexValidator(
                regex=r'^[\w\s]+$',  # Allows alphanumeric characters and spaces
                message="Username can only contain letters, numbers, and spaces."
            )
        ]
        username_field.max_length = 150  # Ensure this matches your database configuration
        username_field.help_text = "Username can contain letters, numbers, and spaces."
