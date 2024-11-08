# signals.py

# from django.db.models.signals import post_save
# from django.dispatch import receiver
# from .models import Folder
# from django.contrib.auth.models import User

# @receiver(post_save, sender=User)
# def create_default_folders(sender, instance, created, **kwargs):
#     if created:
#         # Create default folders
#         Folder.objects.create(user=instance, name='Documents')
#         Folder.objects.create(user=instance, name='Images')
#         Folder.objects.create(user=instance, name='Videos')

# accounts/signals.py
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.contrib.auth.models import User
import os

@receiver(post_save, sender=User)
def create_default_folders(sender, instance, created, **kwargs):
    if created:
        # Define the folder paths for the new user
        user_folder = os.path.join('path_to_user_folders', str(instance.username))
        default_folders = ['Documents', 'Images', 'Videos']

        # Create the main user directory if it doesn't exist
        if not os.path.exists(user_folder):
            os.makedirs(user_folder)

        # Create each default folder
        for folder in default_folders:
            folder_path = os.path.join(user_folder, folder)
            if not os.path.exists(folder_path):
                os.makedirs(folder_path)

