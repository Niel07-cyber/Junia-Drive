from django import template

register = template.Library()

@register.filter
def get_file_preview(file):
    if file.name.endswith(('jpg', 'jpeg', 'png', 'gif')):
        return 'image_preview'
    elif file.name.endswith('pdf'):
        return 'pdf_preview'
    elif file.name.endswith(('mp3', 'wav', 'ogg')):
        return 'audio_preview'
    elif file.name.endswith(('mp4', 'avi', 'mov')):
        return 'video_preview'
    elif file.name.endswith(('txt', 'html', 'py', 'js', 'css')):
        return 'text_preview'
    return None
