from django import forms
from .models import Folder,File

class FolderForm(forms.ModelForm):
    class Meta:
        model = Folder
        fields = ['name']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-input w-full border-gray-300 rounded-lg p-2'})
        }

class FileUploadForm(forms.ModelForm):
    class Meta:
        model = File
        fields = ['file']
    
    def clean_file(self):
        file = self.cleaned_data.get('file')
        max_size = 40 * 1024 * 1024  # 40MB
        if file.size > max_size:
            raise forms.ValidationError("File size exceeds the 40MB limit.")
        return file
    
# class MoveCopyFileForm(forms.Form):
#     target_folder = forms.ModelChoiceField(
#         queryset=Folder.objects.none(),  # Empty initially, set in the view
#         label="Select Target Folder",
#         required=True
#     )

#     def __init__(self, *args, **kwargs):
#         user = kwargs.pop('user', None)  # Get the user from kwargs
#         super().__init__(*args, **kwargs)
#         if user:
#             # Limit folders to those owned by the current user
#             self.fields['target_folder'].queryset = Folder.objects.filter(user=user)

class MoveFileForm(forms.Form):
    target_folder = forms.ModelChoiceField(
        queryset=Folder.objects.none(),  # Will be set in the view based on the user
        label="Select Target Folder",
        required=True
    )

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)
        super().__init__(*args, **kwargs)
        if user:
            # Show only folders that belong to the current user
            self.fields['target_folder'].queryset = Folder.objects.filter(user=user)