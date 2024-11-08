from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver
import uuid
from django.conf import settings

class Folder(models.Model):
    name = models.CharField(max_length=255)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='folders')
    
    def get_share_url(self):
        return f"{settings.SITE_URL}/share/{self.share_link}"

    def __str__(self):
        return self.name

class File(models.Model):
    name = models.CharField(max_length=255)
    folder = models.ForeignKey(Folder, on_delete=models.CASCADE, related_name='files')
    file = models.FileField(upload_to='user_files/')
    # uploaded_at = models.DateTimeField(auto_now_add=True)
    size = models.IntegerField()  # Track file size for storage limit
    share_link = models.UUIDField(default=uuid.uuid4, unique=True, editable=False, null=True, blank=True)
    shared = models.BooleanField(default=False)


    def get_preview_type(self):
        # Assuming `self.file` is a FileField or equivalent
        if self.file.name.endswith(('.png', '.jpg', '.jpeg', '.gif')):
            return 'image_preview'
        elif self.file.name.endswith('.pdf'):
            return 'pdf_preview'
        elif self.file.name.endswith(('.mp3', '.wav')):
            return 'audio_preview'
        elif self.file.name.endswith(('.mp4', '.mov', '.avi')):
            return 'video_preview'
        elif self.file.name.endswith('.txt'):
            return 'text_preview'
        else:
            return 'download'

    def __str__(self):
        return self.name
    

    
# Signal to create default folders

# @receiver(post_save, sender=User)
# def create_default_folders(sender, instance, created, **kwargs):
#     if created:
#         Folder.objects.create(name='Documents', user=instance)
#         Folder.objects.create(name='Images', user=instance)
#         Folder.objects.create(name='Videos', user=instance)


@receiver(post_save, sender=User)
def create_default_folders(sender, instance, created, **kwargs):
    if created:
        print("Creating default folders for new user:", instance.username)
        Folder.objects.create(name='Documents', user=instance)
        Folder.objects.create(name='Images', user=instance)
        Folder.objects.create(name='Videos', user=instance)
        print("Default folders created")
