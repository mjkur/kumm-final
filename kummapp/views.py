from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponse
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Patient, Appointment, MedicalRecord, Doctor
from .forms import PatientForm, AppointmentForm, MedicalRecordForm
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.forms import AuthenticationForm, UserCreationForm
from django.urls import reverse
import datetime
from django.contrib import messages 
from django.db.models import Q 
from django.utils import timezone
from functools import reduce
import operator

# Custom Decorators
def doctor_required(function):
    def wrap(request, *args, **kwargs):
        if not hasattr(request.user, 'doctor'):
            messages.error(request, "You do not have permission to perform this action. Doctor access required.")
            return redirect('index') 
        return function(request, *args, **kwargs)
    wrap.__doc__ = function.__doc__
    wrap.__name__ = function.__name__
    return wrap

# Create your views here.
@login_required
def index(request):
    if not request.user.is_authenticated:
        return redirect('login')  # Redirect to login if user is not authenticated

    today = timezone.now().date()
    todays_appointments = Appointment.objects.filter(appointment_date__date=today).count()
    new_patients_today = Patient.objects.filter(user__date_joined__date=today).count() 
    
    pending_check_ins = Appointment.objects.filter(appointment_date__date=today, appointment_date__gte=timezone.now()).count()

    context = {
        'todays_appointments': todays_appointments,
        'new_patients_today': new_patients_today,
        'pending_check_ins': pending_check_ins,
    }
    return render(request, 'kummapp/index.html', context)


@login_required
def appointment_list(request):
    appointments = Appointment.objects.all().order_by('-appointment_date') # Get all appointments, newest first
    return render(request, 'kummapp/appointment_list.html', {'appointments': appointments})

@login_required
def view_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    return render(request, 'kummapp/view_appointment.html', {'appointment': appointment})

@login_required
def add_appointment(request):
    if request.method == 'POST':
        form = AppointmentForm(request.POST)
        if form.is_valid():
            appointment = form.save()
            messages.success(request, f"Appointment for {appointment.patient} with Dr. {appointment.doctor.last_name} on {appointment.appointment_date.strftime('%Y-%m-%d %H:%M')} scheduled successfully.")
            return redirect('view_appointment', appointment_id=appointment.id)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = AppointmentForm()
    return render(request, 'kummapp/add_appointment.html', {'form': form})

@login_required
def edit_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    if request.method == 'POST':
        form = AppointmentForm(request.POST, instance=appointment)
        if form.is_valid():
            form.save()
            messages.success(request, f"Appointment for {appointment.patient} updated successfully.")
            return redirect('view_appointment', appointment_id=appointment.id)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = AppointmentForm(instance=appointment)
    return render(request, 'kummapp/edit_appointment.html', {'form': form, 'appointment': appointment})

@login_required
def delete_appointment(request, appointment_id):
    appointment = get_object_or_404(Appointment, id=appointment_id)
    if request.method == 'POST':
        appointment_info = f"Appointment for {appointment.patient} with Dr. {appointment.doctor.last_name} on {appointment.appointment_date.strftime('%Y-%m-%d %H:%M')}"
        appointment.delete()
        messages.success(request, f"{appointment_info} cancelled successfully.")
        return redirect('appointment_list')
    return render(request, 'kummapp/delete_appointment_confirm.html', {'appointment': appointment})
