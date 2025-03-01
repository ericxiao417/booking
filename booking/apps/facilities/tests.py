"""
Tests for the facilities app.
"""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone

from booking.apps.facilities.models import Facility
from booking.apps.facilities.forms import FacilityFilterForm, FacilityForm

User = get_user_model()


class FacilityModelTest(TestCase):
    """Test the Facility model."""

    def setUp(self):
        """Set up test data."""
        self.facility = Facility.objects.create(
            name="Test Facility",
            location="Test Location",
            capacity=10,
            description="Test Description",
            opening_time=timezone.now().time(),
            closing_time=(timezone.now() + timezone.timedelta(hours=8)).time(),
        )

    def test_facility_creation(self):
        """Test that a facility can be created."""
        self.assertEqual(self.facility.name, "Test Facility")
        self.assertEqual(self.facility.location, "Test Location")
        self.assertEqual(self.facility.capacity, 10)
        self.assertEqual(self.facility.description, "Test Description")
        self.assertTrue(self.facility.is_active)

    def test_string_representation(self):
        """Test the string representation."""
        self.assertEqual(str(self.facility), "Test Facility")


class FacilityFormTest(TestCase):
    """Test the Facility form."""

    def test_valid_form(self):
        """Test that a valid form validates."""
        data = {
            'name': 'Test Facility',
            'location': 'Test Location',
            'capacity': 10,
            'description': 'Test Description',
            'is_active': True,
        }
        form = FacilityForm(data=data)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        """Test that an invalid form doesn't validate."""
        # Missing required field
        data = {
            'name': '',
            'location': 'Test Location',
            'capacity': 10,
        }
        form = FacilityForm(data=data)
        self.assertFalse(form.is_valid())

        # Invalid capacity (negative)
        data = {
            'name': 'Test Facility',
            'location': 'Test Location',
            'capacity': -1,
        }
        form = FacilityForm(data=data)
        self.assertFalse(form.is_valid())


class FacilityListViewTest(TestCase):
    """Test the facility list view."""

    def setUp(self):
        """Set up test data."""
        self.facility1 = Facility.objects.create(
            name="Facility One",
            location="Location One",
            capacity=10,
            description="Description One",
        )
        self.facility2 = Facility.objects.create(
            name="Facility Two",
            location="Location Two",
            capacity=20,
            description="Description Two",
        )
        self.url = reverse('facilities:facility_list')

    def test_view_url_exists(self):
        """Test that the URL exists."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        """Test that the view uses the correct template."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'facilities/facility_list.html')

    def test_displays_all_facilities(self):
        """Test that all active facilities are displayed."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Facility One")
        self.assertContains(response, "Facility Two")


class FacilityDetailViewTest(TestCase):
    """Test the facility detail view."""

    def setUp(self):
        """Set up test data."""
        self.facility = Facility.objects.create(
            name="Test Facility",
            location="Test Location",
            capacity=10,
            description="Test Description",
        )
        self.url = reverse('facilities:facility_detail', args=[self.facility.pk])

    def test_view_url_exists(self):
        """Test that the URL exists."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        """Test that the view uses the correct template."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'facilities/facility_detail.html')

    def test_displays_facility_details(self):
        """Test that facility details are displayed."""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Facility")
        self.assertContains(response, "Test Location")
        self.assertContains(response, "10")
        self.assertContains(response, "Test Description")


class FacilityCreateViewTest(TestCase):
    """Test the facility create view."""

    def setUp(self):
        """Set up test data."""
        self.url = reverse('facilities:facility_create')
        # Create a staff user
        self.staff_user = User.objects.create_user(
            username='staffuser',
            email='staff@example.com',
            password='password',
            is_staff=True
        )
        # Create a normal user
        self.normal_user = User.objects.create_user(
            username='normaluser',
            email='normal@example.com',
            password='password'
        )

    def test_view_requires_login(self):
        """Test that the view requires login."""
        response = self.client.get(self.url)
        # Should redirect to login page
        self.assertEqual(response.status_code, 302)

    def test_view_requires_staff(self):
        """Test that the view requires staff."""
        # Login as normal user
        self.client.login(username='normaluser', password='password')
        response = self.client.get(self.url)
        # Should be forbidden
        self.assertEqual(response.status_code, 403)

    def test_view_accessible_by_staff(self):
        """Test that the view is accessible by staff."""
        # Login as staff user
        self.client.login(username='staffuser', password='password')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        """Test that the view uses the correct template."""
        # Login as staff user
        self.client.login(username='staffuser', password='password')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'facilities/facility_form.html')

    def test_can_create_facility(self):
        """Test that a facility can be created."""
        # Login as staff user
        self.client.login(username='staffuser', password='password')
        # Create a facility
        data = {
            'name': 'New Facility',
            'location': 'New Location',
            'capacity': 30,
            'description': 'New Description',
            'is_active': True,
        }
        response = self.client.post(self.url, data)
        # Should redirect to facility list
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('facilities:facility_list'))
        # Check if facility was created
        self.assertTrue(Facility.objects.filter(name='New Facility').exists())
