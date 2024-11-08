from django.urls import path
from . import views
from django.contrib.auth.views import LogoutView
from .views import generate_share_link, share_file_view

urlpatterns = [
     path('login/', views.user_login, name='login'),
    path('', views.signup, name='signup'),
    path('home/', views.home, name='home'),
    path('logout/', LogoutView.as_view(next_page='/login/'), name='logout'),
     path('folders/', views.folder_list, name='folder_list'),
    # path('folders/<int:folder_id>/upload/', views.upload_file, name='upload_file'),
    path('folders/<int:folder_id>/', views.folder_detail, name='folder_detail'),
     path('create_folder/', views.create_folder, name='create_folder'),
      
  
    path('folders/<int:folder_id>/upload/', views.file_upload, name='file_upload'),
    path('file/<int:file_id>/delete/', views.delete_file, name='delete_file'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('file/<int:file_id>/move/', views.move_file, name='move_file'),
    path('file/<int:file_id>/copy/', views.copy_file, name='copy_file'),
    path('folder/<int:folder_id>/delete/', views.delete_folder, name='delete_folder'),
    path('file/<int:file_id>/generate_share_link/', generate_share_link, name='generate_share_link'),
    path('share/<uuid:share_link>/', share_file_view, name='share_file_view'),
    # path('file/<int:file_id>/share/', views.share_file, name='share_file'),
    # path('accounts/file/<uuid:file_id>/share/', views.share_file, name='share_file'), 
    #  path('file/<int:file_id>/move/', views.move_file, name='move_file'),

 ]
