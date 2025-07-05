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
def patient_search_view(request):
    query = request.GET.get('query', '').strip()
    patients = Patient.objects.none() 

    if query:
        search_terms = query.split()
        if search_terms:
            term_queries = []
            for term in search_terms:
                term_queries.append(Q(first_name__icontains=term) | Q(last_name__icontains=term))
            
            if term_queries:
                combined_q = reduce(operator.and_, term_queries)
                patients = Patient.objects.filter(combined_q)

        if patients.count() == 1:
            # If exactly one patient matches, redirect to their detail page
            return redirect('patient_detail', patient_id=patients.first().id)
    
    return render(request, 'kummapp/patient_list.html', {'patients': patients, 'query': query})

@login_required
def calendar_view(request):
    appointments = Appointment.objects.all().order_by('appointment_date')
    context = {
        'appointments': appointments
    }
    return render(request, 'kummapp/calendar.html', context)

def login_view(request):
    if request.method == 'POST':
        form = AuthenticationForm(request, data=request.POST)
        if form.is_valid():
            username = form.cleaned_data.get('username')
            password = form.cleaned_data.get('password')
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
                messages.info(request, f"Welcome back, {username}.")
                # Check if next is in POST data, otherwise redirect to index
                next_url = request.POST.get('next')
                if next_url:
                    return redirect(next_url)
                return redirect('index')
            else:
                messages.error(request, "Invalid username or password.")
        else:
            messages.error(request, "Invalid username or password.") # Or form.errors
    else:
        form = AuthenticationForm()
    return render(request, 'kummapp/login.html', {'form': form, 'next': request.GET.get('next', '')})

def logout_view(request):
    logout(request)
    messages.info(request, "You have been successfully logged out.")
    return redirect('login')

@login_required
def new_patient(request):
    if request.method == 'POST':
        form = PatientForm(request.POST)
        if form.is_valid():
            patient = form.save()
            messages.success(request, f"Patient {patient.first_name} {patient.last_name} added successfully.")
            return redirect('patient_detail', patient_id=patient.id)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PatientForm()
    return render(request, 'kummapp/new_patient.html', {'form': form})

@login_required
def edit_patient(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    if request.method == 'POST':
        form = PatientForm(request.POST, instance=patient)
        if form.is_valid():
            form.save()
            messages.success(request, f"Patient {patient.first_name} {patient.last_name} updated successfully.")
            return redirect('patient_detail', patient_id=patient.id)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = PatientForm(instance=patient)
    return render(request, 'kummapp/edit_patient.html', {'form': form, 'patient': patient})

@login_required
def delete_patient(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    if request.method == 'POST':
        patient_name = f"{patient.first_name} {patient.last_name}"
        patient.delete()
        messages.success(request, f"Patient {patient_name} deleted successfully.")
        return redirect('patient_list')
    return render(request, 'kummapp/delete_patient_confirm.html', {'patient': patient})

@login_required
def patient_list(request):
    patients = Patient.objects.all()
    return render(request, 'kummapp/patient_list.html', {'patients': patients})

@login_required
def patient_detail(request, patient_id):
    patient = Patient.objects.get(id=patient_id)
    appointments = Appointment.objects.filter(patient=patient).order_by('-appointment_date')
    medical_records = MedicalRecord.objects.filter(patient=patient).order_by('-visit_date')
    context = {
        'patient': patient,
        'appointments': appointments,
        'medical_records': medical_records
    }
    return render(request, 'kummapp/patient_detail.html', context)

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

<<<<<<< HEAD

=======
>>>>>>> other-backend
# Medical Record Views
@login_required
@doctor_required
def add_medical_record(request, patient_id):
    patient = get_object_or_404(Patient, id=patient_id)
    if request.method == 'POST':
        form = MedicalRecordForm(request.POST, user=request.user) 
        if form.is_valid():
            record = form.save(commit=False)
            record.patient = patient
            record.save()
            messages.success(request, f"Medical record for {patient.first_name} {patient.last_name} added successfully.")
            return redirect('patient_detail', patient_id=patient.id)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = MedicalRecordForm(user=request.user)
    return render(request, 'kummapp/add_medical_record.html', {'form': form, 'patient': patient})

@login_required
def edit_medical_record(request, record_id):
    record = get_object_or_404(MedicalRecord, id=record_id)
    can_edit = False
    if request.user.is_staff:
        can_edit = True
    elif hasattr(request.user, 'doctor') and record.doctor == request.user.doctor:
        can_edit = True

    if not can_edit:
        messages.error(request, "You do not have permission to edit this medical record.")
        return redirect('patient_detail', patient_id=record.patient.id)

    if request.method == 'POST':
        form = MedicalRecordForm(request.POST, instance=record, user=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, "Medical record updated successfully.")
            return redirect('patient_detail', patient_id=record.patient.id)
        else:
            messages.error(request, "Please correct the errors below.")
    else:
        form = MedicalRecordForm(instance=record, user=request.user)
    return render(request, 'kummapp/edit_medical_record.html', {'form': form, 'record': record, 'patient': record.patient})

@login_required
def delete_medical_record(request, record_id):
    record = get_object_or_404(MedicalRecord, id=record_id)
    patient_id = record.patient.id
    can_delete = False
    if request.user.is_staff:
        can_delete = True
    elif hasattr(request.user, 'doctor') and record.doctor == request.user.doctor:
        can_delete = True

    if not can_delete:
        messages.error(request, "You do not have permission to delete this medical record.")
        return redirect('patient_detail', patient_id=patient_id)

    if request.method == 'POST':
        record.delete()
        messages.success(request, "Medical record deleted successfully.")
        return redirect('patient_detail', patient_id=patient_id)
    return render(request, 'kummapp/delete_medical_record_confirm.html', {'record': record, 'patient': record.patient})
<<<<<<< HEAD
=======

# Auth Views
def register_view(request):
    # TODO: nieużywane na razie
    if request.method == 'POST':
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user) # Log in the user automatically after registration
            messages.success(request, "Registration successful. You are now logged in.")
            # Redirect to a page to create a Doctor profile or to index
            # For now, redirect to index. A more complete flow would guide Doctor creation.
            return redirect('index') 
        else:
            messages.error(request, "Registration unsuccessful. Please correct the errors below.")
    else:
        form = UserCreationForm()
    return render(request, 'registration/register.html', {'form': form})
>>>>>>> other-backend
