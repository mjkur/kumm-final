from django import forms
from .models import Patient, Appointment, Doctor, MedicalRecord

class PatientForm(forms.ModelForm):
    class Meta:
        model = Patient
        fields = ['first_name', 'last_name', 'date_of_birth', 'address', 'phone_number', 'email']
        widgets = {
            'date_of_birth': forms.DateInput(attrs={'type': 'date'}),
        }

class AppointmentForm(forms.ModelForm):
    class Meta:
        model = Appointment
        fields = ['patient', 'doctor', 'appointment_date', 'reason', 'notes']
        widgets = {
            'appointment_date': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['patient'].queryset = Patient.objects.all()
        self.fields['doctor'].queryset = Doctor.objects.all()

class MedicalRecordForm(forms.ModelForm):
    class Meta:
        model = MedicalRecord
        fields = ['patient', 'doctor', 'visit_date', 'diagnosis', 'treatment', 'notes']
        widgets = {
            'visit_date': forms.DateInput(attrs={'type': 'date'}),
            'diagnosis': forms.Textarea(attrs={'rows': 3}),
            'treatment': forms.Textarea(attrs={'rows': 3}),
            'notes': forms.Textarea(attrs={'rows': 3}),
        }

    def __init__(self, *args, **kwargs):
        user = kwargs.pop('user', None)  # Expect 'user' to be passed from the view
        super().__init__(*args, **kwargs)
        
        self.fields['patient'].queryset = Patient.objects.all()
        self.fields['doctor'].queryset = Doctor.objects.all()
        
        if user and hasattr(user, 'doctor'):
            # If creating a new record (no instance or instance without pk)
            if not self.instance or not self.instance.pk:
                self.initial['doctor'] = user.doctor # Pre-fill with logged-in doctor
            # Always disable the doctor field if the logged-in user is a doctor
            self.fields['doctor'].disabled = True
