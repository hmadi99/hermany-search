from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from . import views

urlpatterns = [
   
    path('', views.Login_view, name='Login_view'),
    path('manage-users/', views.manage_users, name='manage_users'),
    path('add-user/', views.add_user, name='add_user'),
    path('edit-user/<int:user_id>/', views.edit_user, name='edit_user'),
    path('delete-user/<int:user_id>/', views.delete_user, name='delete_user'),
    path('home/', views.home, name='home'),
    path('manage_colleges/', views.manage_colleges, name='manage_colleges'),
    path('edit_college/<int:college_id>/', views.edit_college, name='edit_college'),
    path('add_lecturer/', views.add_lecturer, name='add_lecturer'),
    path('delete-lecturer/<int:lecturer_id>/', views.delete_lecturer, name='delete_lecturer'),
    path('add_department/', views.add_department, name='add_department'),
    path('delete-department/<int:department_id>/', views.delete_department, name='delete_department'),
    path('add_room/', views.add_room, name='add_room'),
    path('choose/', views.choose, name='choose'),
    path('delete-room/<int:room_id>/', views.delete_room, name='delete_room'),
    path('add_course/', views.add_course, name='add_course'),
    path('edit-course/<int:course_id>/', views.edit_course, name='edit_course'),
    path('delete-course/<int:course_id>/', views.delete_course, name='delete_course'),
    path('term/', views.term, name='term'),
    path('generate_schedule/', views.generate_schedule, name='generate_schedule'),
    path('generate_schedule_final/', views.generate_schedule_final, name='generate_schedule_final'),
    path("export_schedule/", views.export_schedule_to_excel, name="export_schedule_to_excel"),
    path('export_schedule_to_pdf/', views.export_schedule_to_pdf, name='export_schedule_to_pdf'),
]+ static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

