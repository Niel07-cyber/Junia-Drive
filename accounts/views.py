

# Create your views here.
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import authenticate, login
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.contrib import messages
import os
from django.conf import settings
from .models import Folder, File
from .forms import FolderForm 
from .forms import FileUploadForm
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseRedirect
from django.urls import reverse  # Add this import
from django.db.models import Count, Q,Sum
# from .forms import MoveCopyFileForm
from .forms import MoveFileForm
import uuid


def signup(request):
    if request.method == 'POST':
        username = request.POST['username']
        email = request.POST['email']
        password = request.POST['password']
        
        # Check if passwords match
        if password != request.POST['cpassword']:
            messages.error(request, "Passwords do not match.")
            return redirect('signup')
        
        try:
            # Create the user
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()
            
            # Create a folder for the new user
            user_folder_path = os.path.join(settings.MEDIA_ROOT, 'user_folders', str(user.id))
            if not os.path.exists(user_folder_path):
                os.makedirs(user_folder_path)  # Creates the user's folder

            # Add success message
            messages.success(request, "Signup successful! Please log in.")
            return redirect('login')
        except Exception as e:
            messages.error(request, f"Error creating account: {e}")
    
    return render(request, 'accounts/signup.html')


def user_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # Authenticate the user
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            messages.success(request, "Login successful!")
            return redirect('home')  # or any page where you want to redirect after login
        else:
            messages.error(request, "Invalid username or password.")

    return render(request, 'accounts/login.html')


# def home(request):
#     return render(request, 'accounts/home.html')


# def home(request):
#     # Ensure the user is authenticated
#     if request.user.is_authenticated:
#         folders = Folder.objects.filter(user=request.user)
#     else:
#         folders = []
    
#     return render(request, 'accounts/home.html', {'folders': folders})

@login_required(login_url='/login/')  # Ensures only logged-in users can access this view
def home(request):
    # Check if the user is authenticated before querying
    if not request.user.is_authenticated:
        return redirect('login')

    # Now it’s safe to retrieve folders for the authenticated user
    folders = Folder.objects.filter(user=request.user)
    return render(request, 'accounts/home.html', {'folders': folders})


# here
def folder_list(request):
    folders = Folder.objects.filter(user=request.user)
    return render(request, 'accounts/folder_list.html', {'folders': folders})

def upload_file(request, folder_id):
    folder = get_object_or_404(Folder, id=folder_id, user=request.user)
    if request.method == 'POST':
        uploaded_file = request.FILES['file']
        
        # Enforce file size and storage limits here
        max_file_size = 40 * 1024 * 1024
        if uploaded_file.size > max_file_size:
            messages.error(request, "File too large! Maximum size is 40MB.")
            return redirect('folder_list')

        # Create a new File object
        File.objects.create(
            name=uploaded_file.name,
            folder=folder,
            file=uploaded_file,
            size=uploaded_file.size,
        )
        messages.success(request, "File uploaded successfully.")
        return redirect('folder_list')

    return render(request, 'accounts/upload_file.html', {'folder': folder})



def file_upload(request, folder_id):
    folder = get_object_or_404(Folder, id=folder_id, user=request.user)
    
    if request.method == 'POST':
        if 'file' in request.FILES:
            uploaded_file = request.FILES['file']
            max_file_size = 40 * 1024 * 1024  # 40 MB limit
            
            # Check if file size exceeds limit
            if uploaded_file.size > max_file_size:
                messages.error(request, "File too large! Maximum size is 40MB.")
                return redirect('folder_detail', folder_id=folder.id)

            # Save file with FileSystemStorage
            fs = FileSystemStorage()
            filename = fs.save(uploaded_file.name, uploaded_file)
            
            # Create File object
            File.objects.create(
                name=filename,
                folder=folder,
                file=uploaded_file,
                size=uploaded_file.size
            )
            messages.success(request, "File uploaded successfully.")
            return redirect('folder_detail', folder_id=folder.id)

    return render(request, 'accounts/upload_file.html', {'folder': folder})


# def folder_detail(request, folder_id):
#     folder = get_object_or_404(Folder, id=folder_id, user=request.user)
#     files = folder.files.all()  # Assuming a `related_name='files'` in the File model
#     return render(request, 'accounts/folder_detail.html', {'folder': folder, 'files': files})

MAX_UPLOAD_SIZE = 40 * 1024 * 1024  # 40 MB

# def folder_detail(request, folder_id):
#     folder = get_object_or_404(Folder, id=folder_id, user=request.user)
#     files = folder.files.all()
    
#     file_previews = []
#     for file in files:
#         preview_type = None
#         if file.name.endswith(('jpg', 'jpeg', 'png', 'gif')):
#             preview_type = 'image_preview'
#         elif file.name.endswith('pdf'):
#             preview_type = 'pdf_preview'
#         elif file.name.endswith(('mp3', 'wav', 'ogg')):
#             preview_type = 'audio_preview'
#         elif file.name.endswith(('mp4', 'avi', 'mov')):
#             preview_type = 'video_preview'
#         elif file.name.endswith(('txt', 'html', 'py', 'js', 'css')):
#             preview_type = 'text_preview'
        
#         file_previews.append({'file': file, 'preview_type': preview_type})

#     return render(request, 'accounts/folder_detail.html', {'folder': folder, 'file_previews': file_previews})


# def folder_detail(request, folder_id):
#     folder = get_object_or_404(Folder, id=folder_id, user=request.user)
#     files = folder.files.all()

#     # Define the default folder names
#     default_folder_names = ["Documents", "Images", "Videos"]

#     # Initialize counts for each default folder with zero
#     default_folder_counts = {name: 0 for name in default_folder_names}
    
#     # Count files in each default folder and update the dictionary
#     default_counts = (
#         File.objects
#         .filter(folder__name__in=default_folder_names, folder__user=request.user)
#         .values('folder__name')
#         .annotate(count=Count('id'))
#     )

#     # Update default folder counts with actual counts from the query
#     for item in default_counts:
#         default_folder_counts[item['folder__name']] = item['count']

#     # Count files in user-created folders (Others)
#     others_count = File.objects.filter(
#         ~Q(folder__name__in=default_folder_names),  # Exclude default folders
#         folder__user=request.user
#     ).count()
    
#     # Add "Others" to the dictionary
#     default_folder_counts['Others'] = others_count

#     # Process previews for each file (as previously done)
#     file_previews = []
#     for file in files:
#         if file.name.endswith(('jpg', 'jpeg', 'png', 'gif')):
#             preview_type = 'image_preview'
#         elif file.name.endswith('pdf'):
#             preview_type = 'pdf_preview'
#         elif file.name.endswith(('mp3', 'wav', 'ogg')):
#             preview_type = 'audio_preview'
#         elif file.name.endswith(('mp4', 'avi', 'mov')):
#             preview_type = 'video_preview'
#         elif file.name.endswith(('txt', 'html', 'py', 'js', 'css')):
#             preview_type = 'text_preview'
#         else:
#             preview_type = None

#         file_previews.append({'file': file, 'preview_type': preview_type})

#     # Pass folder counts to the template
#     return render(
#         request,
#         'accounts/folder_detail.html',
#         {
#             'folder': folder,
#             'file_previews': file_previews,
#             'folder_counts': default_folder_counts
#         }
#     )



# def folder_detail(request, folder_id):
#     folder = get_object_or_404(Folder, id=folder_id, user=request.user)
#     files = folder.files.all()
#     folders = Folder.objects.filter(user=request.user).exclude(id=folder_id)
#     # Define the default folder names
#     default_folder_names = ["Documents", "Images", "Videos"]

#     # Initialize counts for each default folder with zero
#     default_folder_counts = {name: 0 for name in default_folder_names}

#     # Count files in each default folder and update the dictionary
#     default_counts = (
#         File.objects
#         .filter(folder__name__in=default_folder_names, folder__user=request.user)
#         .values('folder__name')
#         .annotate(count=Count('id'))
#     )

#     # Update default folder counts with actual counts from the query
#     for item in default_counts:
#         default_folder_counts[item['folder__name']] = item['count']

#     # Count files in user-created folders (Others)
#     others_count = File.objects.filter(
#         ~Q(folder__name__in=default_folder_names),  # Exclude default folders
#         folder__user=request.user
#     ).count()

#     # Add "Others" to the dictionary
#     default_folder_counts['Others'] = others_count

#     # Process previews for each file using get_preview_type
#     file_previews = [{'file': file, 'preview_type': file.get_preview_type()} for file in files]

#     # Pass folder counts to the template
#     return render(
#         request,
#         'accounts/folder_detail.html',
#         {
#             'folder': folder,
#             'file_previews': file_previews,
#             'folder_counts': default_folder_counts
#         }
#     )


from django.shortcuts import render, get_object_or_404
from django.db.models import Count, Q
from .models import Folder, File

def folder_detail(request, folder_id):
    # Get the current folder and files
    folder = get_object_or_404(Folder, id=folder_id, user=request.user)
    files = folder.files.all()

    # List of folders for the move modal, excluding the current folder
    folders = Folder.objects.filter(user=request.user).exclude(id=folder_id)

    # Default folder names for categorization
    default_folder_names = ["Documents", "Images", "Videos"]

    # Initialize default folder counts with zero
    default_folder_counts = {name: 0 for name in default_folder_names}

    # Count files for each default folder
    default_counts = (
        File.objects
        .filter(folder__name__in=default_folder_names, folder__user=request.user)
        .values('folder__name')
        .annotate(count=Count('id'))
    )

    # Update default folder counts with actual counts from the query
    for item in default_counts:
        default_folder_counts[item['folder__name']] = item['count']

    # Count files in user-created folders (Others)
    others_count = File.objects.filter(
        ~Q(folder__name__in=default_folder_names),
        folder__user=request.user
    ).count()
    default_folder_counts['Others'] = others_count

    # Prepare file previews with their preview types
    file_previews = [{'file': file, 'preview_type': file.get_preview_type()} for file in files]

    # Render the template with all required context
    return render(
        request,
        'accounts/folder_detail.html',
        {
            'folder': folder,
            'file_previews': file_previews,
            'folder_counts': default_folder_counts,
            'folders': folders  # Add this for the move modal
        }
    )



def create_folder(request):
    if request.method == 'POST':
        form = FolderForm(request.POST)
        if form.is_valid():
            folder = form.save(commit=False)
            folder.user = request.user  # Assign folder to the logged-in user
            folder.save()
            return redirect('home')  # Redirect to home after creating folder
    else:
        form = FolderForm()
    return render(request, 'accounts/create_folder.html', {'form': form})


def upload_file(request, folder_id):
    folder = get_object_or_404(Folder, id=folder_id, user=request.user)
    
    if request.method == 'POST':
        if 'file' in request.FILES:
            uploaded_file = request.FILES['file']
            max_file_size = 40 * 1024 * 1024  # 40 MB
            
            # Check file size
            if uploaded_file.size > max_file_size:
                messages.error(request, "File too large! Maximum size is 40MB.")
                return redirect('folder_detail', folder_id=folder.id)

            # Save file
            File.objects.create(
                name=uploaded_file.name,
                folder=folder,
                file=uploaded_file,
                size=uploaded_file.size
            )
            messages.success(request, "File uploaded successfully.")
            return redirect('folder_detail', folder_id=folder.id)

    # Render the upload file template
    return render(request, 'accounts/upload_file.html', {'folder': folder})


def delete_file(request, file_id):
    file = get_object_or_404(File, id=file_id, folder__user=request.user)

    # Construct the file path manually using MEDIA_ROOT
    file_path = os.path.join(settings.MEDIA_ROOT, file.file.name)

    # Delete the file from storage and the database
    if os.path.exists(file_path):
        os.remove(file_path)  # Manually remove the file from the filesystem
    file.delete()  # Delete the record from the database

    messages.success(request, "File deleted successfully.")
    # Redirect back to the folder detail page after deletion
    return HttpResponseRedirect(reverse('folder_detail', args=[file.folder.id]))


def dashboard(request):
    # Define maximum storage limit in bytes (e.g., 100 MB)
    storage_limit = 100 * 1024 * 1024  # 100 MB in bytes

    # Calculate total space used by summing up file sizes for the current user
    space_used = File.objects.filter(folder__user=request.user).aggregate(total_size=Sum('size'))['total_size'] or 0
    space_remaining = storage_limit - space_used if storage_limit > space_used else 0

    space_used_mb = space_used / (1024 * 1024)
    space_remaining_mb = space_remaining / (1024 * 1024)
    storage_limit_mb = storage_limit / (1024 * 1024)

    # Define folder names and calculate file counts as before
    default_folder_names = ["Documents", "Images", "Videos"]
    folder_counts = {name: 0 for name in default_folder_names}
    
    default_counts = (
        File.objects
        .filter(folder__name__in=default_folder_names, folder__user=request.user)
        .values('folder__name')
        .annotate(count=Count('id'))
    )

    for item in default_counts:
        folder_counts[item['folder__name']] = item['count']

    folder_counts['Others'] = File.objects.filter(
        ~Q(folder__name__in=default_folder_names), folder__user=request.user
    ).count()

    # Pass all data to the dashboard template
    return render(request, 'accounts/dashboard.html', {
        'folder_counts': folder_counts,
        'space_used': space_used_mb,
        'space_remaining': space_remaining_mb,
        'storage_limit': storage_limit_mb
    })

def move_file(request, file_id):
    # Get the file and ensure it belongs to the logged-in user
    file = get_object_or_404(File, id=file_id, folder__user=request.user)
    
    if request.method == 'POST':
        form = MoveFileForm(request.POST, user=request.user)
        if form.is_valid():
            target_folder = form.cleaned_data['target_folder']
            # Update the file's folder to the new target folder
            file.folder = target_folder
            file.save()
            messages.success(request, f"File '{file.name}' moved successfully.")
            return redirect('folder_detail', folder_id=target_folder.id)
    else:
        form = MoveFileForm(user=request.user)

    return render(request, 'accounts/move_file.html', {'form': form, 'file': file})

# def copy_file(request, file_id):
#     # Get the file to be copied and ensure it belongs to the logged-in user
#     file = get_object_or_404(File, id=file_id, folder__user=request.user)
#     folder = file.folder  # The folder where the copy will be placed

#     # Generate a new name to avoid naming conflicts
#     new_name = f"{file.name} (Copy)"
#     count = 1
#     # Check if the new name already exists in the folder and modify if necessary
#     while File.objects.filter(name=new_name, folder=folder).exists():
#         count += 1
#         new_name = f"{file.name} (Copy {count})"

#     # Create a new file entry with the new name
#     File.objects.create(
#         name=new_name,
#         folder=folder,
#         file=file.file,  # Reference the same file data
#         size=file.size
#     )

#     messages.success(request, f"File '{file.name}' copied successfully as '{new_name}'.")
#     return redirect('folder_detail', folder_id=folder.id)


def copy_file(request, file_id):
    # Get the file to be copied and ensure it belongs to the logged-in user
    file = get_object_or_404(File, id=file_id, folder__user=request.user)
    folder = file.folder  # The folder where the copy will be placed

    # Generate a new name to avoid naming conflicts
    new_name = f"{file.name} (Copy)"
    count = 1
    # Check if the new name already exists in the folder and modify if necessary
    while File.objects.filter(name=new_name, folder=folder).exists():
        count += 1
        new_name = f"{file.name} (Copy {count})"

    # Create a new file entry with the new name
    copied_file = File.objects.create(
        name=new_name,
        folder=folder,
        file=file.file,  # Reference the same file data
        size=file.size
    )

    # Use get_preview_type to determine the preview type of the copied file
    copied_file_preview_type = copied_file.get_preview_type()

    messages.success(request, f"File '{file.name}' copied successfully as '{new_name}'.")
    return redirect('folder_detail', folder_id=folder.id)


def delete_folder(request, folder_id):
    folder = get_object_or_404(Folder, id=folder_id, user=request.user)
    if request.method == 'POST':
        folder.delete()
        messages.success(request, f'Folder "{folder.name}" deleted successfully.')
    return redirect('home')



# def generate_share_link(request, file_id):
#     file = get_object_or_404(File, id=file_id, folder__user=request.user)
#     if not file.share_link:
#         file.share_link = uuid.uuid4()
#         file.save()
#     return redirect('share_file', file_id=file.id)

# def generate_share_link(request, file_id):
#     file = get_object_or_404(File, id=file_id, folder__user=request.user)
#     if not file.share_link:
#         file.share_link = uuid.uuid4()
#         file.save()

#     # Generate the correct shareable URL
#     share_url = request.build_absolute_uri(reverse('share_file_view', args=[file.share_link]))

#     return JsonResponse({'share_url': share_url})


def share_file_view(request, share_link):
    file = get_object_or_404(File, share_link=share_link, shared=True)
    return render(request, 'accounts/shared_file_view.html', {'file': file})


# def share_file(request, file_id):
#     file = get_object_or_404(File, id=file_id, folder__user=request.user)
#     share_link = file.share_link
#     return render(request, 'accounts/share_file.html', {'file': file, 'share_link': share_link})

import logging
logger = logging.getLogger(__name__)

def share_file_view(request, share_link):
    # Fetch the file by its unique share link
    file = get_object_or_404(File, share_link=share_link)

    # Determine the type of file and choose the appropriate template
    file_extension = file.name.split('.')[-1].lower()

    # Use different templates or embed options based on file type
    if file_extension in ['jpg', 'jpeg', 'png', 'gif']:
        # Render a template to display an image
        return render(request, 'accounts/share_image.html', {'file': file})
    elif file_extension == 'pdf':
        # Render a template for PDF display
        return render(request, 'accounts/share_pdf.html', {'file': file})
    elif file_extension in ['mp3', 'wav']:
        # Render a template for audio file
        return render(request, 'accounts/share_audio.html', {'file': file})
    elif file_extension in ['mp4', 'mov']:
        # Render a template for video file
        return render(request, 'accounts/share_video.html', {'file': file})
    else:
        # Default to a file download option for unsupported types
        return render(request, 'accounts/share_file_download.html', {'file': file})


from django.http import JsonResponse

def generate_share_link(request, file_id):
    file = get_object_or_404(File, id=file_id, folder__user=request.user)
    if not file.share_link:
        file.share_link = uuid.uuid4()
        file.save()

    # Generate the absolute shareable URL
    share_url = request.build_absolute_uri(reverse('share_file_view', args=[file.share_link]))

    return JsonResponse({'share_url': share_url})



