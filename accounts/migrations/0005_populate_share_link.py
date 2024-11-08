from django.db import migrations, models
import uuid

def populate_unique_share_links(apps, schema_editor):
    File = apps.get_model('accounts', 'File')  # Replace 'accounts' with your actual app name if different
    for file in File.objects.all():
        if not file.share_link:
            file.share_link = uuid.uuid4()
            file.save()

            
def create_default_folders(apps, schema_editor):
    Folder = apps.get_model('accounts', 'Folder')
    User = apps.get_model('auth', 'User')  # Adjust this if you have a custom user model

    default_folder_names = ["Documents", "Images", "Videos"]
    for user in User.objects.all():
        for folder_name in default_folder_names:
            Folder.objects.get_or_create(name=folder_name, user=user)

class Migration(migrations.Migration):

    dependencies = [
        ('accounts', '0004_file_share_link_file_shared'),  # Adjust to match your last migration
    ]

    operations = [
        migrations.RunPython(populate_unique_share_links),
        migrations.RunPython(create_default_folders),  # Run the default folder creation
    ]