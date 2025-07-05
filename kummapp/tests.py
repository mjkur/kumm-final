from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from .models import Patient
from django.utils import timezone
import datetime

# Create your tests here.

class PatientModelTests(TestCase):
    def test_create_patient(self):
        """
        Test that a Patient can be created.
        """
        patient = Patient.objects.create(
            first_name="John",
            last_name="Doe",
            date_of_birth=datetime.date(1990, 1, 1),
            address="123 Main St",
            phone_number="555-1234",
            email="john.doe@example.com"
        )
        self.assertEqual(str(patient), "John Doe")
        self.assertEqual(Patient.objects.count(), 1)

class ViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = User.objects.create_user(username='testuser', password='password123')
        self.patient = Patient.objects.create(
            first_name="Alice",
            last_name="Smith",
            date_of_birth=datetime.date(1985, 5, 15),
            address="456 Oak Ave",
            phone_number="555-5678",
            email="alice.smith@example.com"
        )

    def test_index_view_unauthenticated(self):
        """
        Test that the index view redirects to login for unauthenticated users.
        """
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"{reverse('login')}?next={reverse('index')}")

    def test_index_view_authenticated(self):
        """
        Test that the index view is accessible to authenticated users.
        """
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('index'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'kummapp/index.html')
        self.assertIn('todays_appointments', response.context)
        self.assertIn('new_patients_today', response.context)
        self.assertIn('pending_check_ins', response.context)


    def test_patient_search_view_get(self):
        """
        Test that the patient search view is accessible via GET.
        """
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('patient_search'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'kummapp/patient_list.html')

    def test_patient_search_view_finds_patient(self):
        """
        Test that the patient search view redirects to the detail page when a single patient is found by full name.
        """
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('patient_search'), {'query': 'Alice Smith'})
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('patient_detail', kwargs={'patient_id': self.patient.id}))

    def test_patient_search_view_no_results(self):
        """
        Test that the patient search view returns no results for a non-existent patient.
        """
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('patient_search'), {'query': 'NonExistentName'})
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "No patients found matching")
        self.assertEqual(len(response.context['patients']), 0)

    def test_patient_search_view_redirects_on_single_match(self):
        """
        Test that the patient search view redirects to patient_detail if only one patient is found.
        """
        self.client.login(username='testuser', password='password123')
        response = self.client.get(reverse('patient_search'), {'query': 'Smith'})
        self.assertEqual(response.status_code, 302) 
        self.assertRedirects(response, reverse('patient_detail', kwargs={'patient_id': self.patient.id}))
