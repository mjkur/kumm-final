from django.contrib import admin
from django.urls import path
from . import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('calendar/', views.calendar_view, name='calendar'),
    path('login/', views.login_view, name='login'),
    path('new_patient/', views.new_patient, name='new_patient'),
    path('logout/', views.logout_view, name='logout'),
    path('patients/', views.patient_list, name='patient_list'),
    path('patients/search/', views.patient_search_view, name='patient_search'),  
    path('patients/<int:patient_id>/', views.patient_detail, name='patient_detail'),
    path('patients/<int:patient_id>/edit/', views.edit_patient, name='edit_patient'),
    path('patients/<int:patient_id>/delete/', views.delete_patient, name='delete_patient'),
    path('appointments/', views.appointment_list, name='appointment_list'),
    path('appointments/add/', views.add_appointment, name='add_appointment'),
    path('appointments/<int:appointment_id>/', views.view_appointment, name='view_appointment'),
    path('appointments/<int:appointment_id>/edit/', views.edit_appointment, name='edit_appointment'),
    path('appointments/<int:appointment_id>/delete/', views.delete_appointment, name='delete_appointment'),
    path('patients/<int:patient_id>/records/add/', views.add_medical_record, name='add_medical_record'),
    path('records/<int:record_id>/edit/', views.edit_medical_record, name='edit_medical_record'),
    path('records/<int:record_id>/delete/', views.delete_medical_record, name='delete_medical_record'),
]