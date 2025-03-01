"""
Tests for the bookings app.
"""
from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone

from booking.apps.bookings.models import Booking
from booking.apps.bookings.forms import BookingForm, BookingFilterForm
from booking.apps.facilities.models import Facility

User = get_user_model()


class BookingModelTest(TestCase):
    """Test the Booking model."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password'
        )
        self.facility = Facility.objects.create(
            name="Test Facility",
            location="Test Location",
            capacity=10,
            description="Test Description",
        )
        # Create a booking in the future
        future_time = timezone.now() + timezone.timedelta(days=1)
        self.booking = Booking.objects.create(
            user=self.user,
            facility=self.facility,
            title="Test Booking",
            description="Test Description",
            start_time=future_time,
            end_time=future_time + timezone.timedelta(hours=2),
            number_of_people=5,
        )

    def test_booking_creation(self):
        """Test that a booking can be created."""
        self.assertEqual(self.booking.title, "Test Booking")
        self.assertEqual(self.booking.description, "Test Description")
        self.assertEqual(self.booking.number_of_people, 5)
        self.assertEqual(self.booking.status, "pending")
        self.assertEqual(self.booking.user, self.user)
        self.assertEqual(self.booking.facility, self.facility)

    def test_string_representation(self):
        """Test the string representation."""
        self.assertIn("Test Booking", str(self.booking))
        self.assertIn("Test Facility", str(self.booking))

    def test_status_methods(self):
        """Test the status methods."""
        # Test confirm method
        self.booking.confirm()
        self.assertEqual(self.booking.status, "confirmed")

        # Test cancel method
        self.booking.cancel()
        self.assertEqual(self.booking.status, "cancelled")


class BookingFormTest(TestCase):
    """Test the Booking form."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password'
        )
        self.facility = Facility.objects.create(
            name="Test Facility",
            location="Test Location",
            capacity=10,
            description="Test Description",
        )
        self.future_time = timezone.now() + timezone.timedelta(days=1)

    def test_valid_form(self):
        """Test that a valid form validates."""
        data = {
            'facility': self.facility.id,
            'title': 'Test Booking',
            'description': 'Test Description',
            'start_time': self.future_time,
            'end_time': self.future_time + timezone.timedelta(hours=2),
            'number_of_people': 5,
        }
        form = BookingForm(data=data, user=self.user)
        self.assertTrue(form.is_valid())

    def test_invalid_form(self):
        """Test that an invalid form doesn't validate."""
        # Past booking
        past_time = timezone.now() - timezone.timedelta(days=1)
        data = {
            'facility': self.facility.id,
            'title': 'Test Booking',
            'description': 'Test Description',
            'start_time': past_time,
            'end_time': past_time + timezone.timedelta(hours=2),
            'number_of_people': 5,
        }
        form = BookingForm(data=data, user=self.user)
        self.assertFalse(form.is_valid())

        # Invalid time range (end before start)
        data = {
            'facility': self.facility.id,
            'title': 'Test Booking',
            'description': 'Test Description',
            'start_time': self.future_time,
            'end_time': self.future_time - timezone.timedelta(hours=1),
            'number_of_people': 5,
        }
        form = BookingForm(data=data, user=self.user)
        self.assertFalse(form.is_valid())

        # Too many people
        data = {
            'facility': self.facility.id,
            'title': 'Test Booking',
            'description': 'Test Description',
            'start_time': self.future_time,
            'end_time': self.future_time + timezone.timedelta(hours=2),
            'number_of_people': 20,  # Capacity is 10
        }
        form = BookingForm(data=data, user=self.user)
        self.assertFalse(form.is_valid())


class BookingListViewTest(TestCase):
    """Test the booking list view."""

    def setUp(self):
        """Set up test data."""
        # Create a regular user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password'
        )
        # Create a staff user
        self.staff_user = User.objects.create_user(
            username='staffuser',
            email='staff@example.com',
            password='password',
            is_staff=True
        )
        self.facility = Facility.objects.create(
            name="Test Facility",
            location="Test Location",
            capacity=10,
            description="Test Description",
        )
        # Create some bookings
        future_time = timezone.now() + timezone.timedelta(days=1)
        self.booking1 = Booking.objects.create(
            user=self.user,
            facility=self.facility,
            title="Booking One",
            start_time=future_time,
            end_time=future_time + timezone.timedelta(hours=2),
            number_of_people=5,
        )
        self.booking2 = Booking.objects.create(
            user=self.staff_user,
            facility=self.facility,
            title="Booking Two",
            start_time=future_time + timezone.timedelta(days=1),
            end_time=future_time + timezone.timedelta(days=1, hours=2),
            number_of_people=3,
        )
        self.url = reverse('bookings:booking_list')

    def test_view_requires_login(self):
        """Test that the view requires login."""
        response = self.client.get(self.url)
        # Should redirect to login page
        self.assertEqual(response.status_code, 302)

    def test_user_sees_only_own_bookings(self):
        """Test that a regular user only sees their own bookings."""
        self.client.login(username='testuser', password='password')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Booking One")
        self.assertNotContains(response, "Booking Two")

    def test_staff_sees_all_bookings(self):
        """Test that a staff user sees all bookings."""
        self.client.login(username='staffuser', password='password')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Booking One")
        self.assertContains(response, "Booking Two")

    def test_view_uses_correct_template(self):
        """Test that the view uses the correct template."""
        self.client.login(username='testuser', password='password')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bookings/booking_list.html')


class BookingDetailViewTest(TestCase):
    """Test the booking detail view."""

    def setUp(self):
        """Set up test data."""
        # Create a regular user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password'
        )
        # Create another user
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='password'
        )
        # Create a staff user
        self.staff_user = User.objects.create_user(
            username='staffuser',
            email='staff@example.com',
            password='password',
            is_staff=True
        )
        self.facility = Facility.objects.create(
            name="Test Facility",
            location="Test Location",
            capacity=10,
            description="Test Description",
        )
        # Create a booking
        future_time = timezone.now() + timezone.timedelta(days=1)
        self.booking = Booking.objects.create(
            user=self.user,
            facility=self.facility,
            title="Test Booking",
            description="Test Description",
            start_time=future_time,
            end_time=future_time + timezone.timedelta(hours=2),
            number_of_people=5,
        )
        self.url = reverse('bookings:booking_detail', args=[self.booking.pk])

    def test_view_requires_login(self):
        """Test that the view requires login."""
        response = self.client.get(self.url)
        # Should redirect to login page
        self.assertEqual(response.status_code, 302)

    def test_owner_can_view_booking(self):
        """Test that the booking owner can view the booking."""
        self.client.login(username='testuser', password='password')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Booking")
        self.assertContains(response, "Test Description")

    def test_other_user_cannot_view_booking(self):
        """Test that other users cannot view the booking."""
        self.client.login(username='otheruser', password='password')
        response = self.client.get(self.url)
        # Should be forbidden
        self.assertEqual(response.status_code, 403)

    def test_staff_can_view_all_bookings(self):
        """Test that staff can view all bookings."""
        self.client.login(username='staffuser', password='password')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Test Booking")
        self.assertContains(response, "Test Description")

    def test_view_uses_correct_template(self):
        """Test that the view uses the correct template."""
        self.client.login(username='testuser', password='password')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bookings/booking_detail.html')


class BookingCreateViewTest(TestCase):
    """Test the booking create view."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='password'
        )
        self.facility = Facility.objects.create(
            name="Test Facility",
            location="Test Location",
            capacity=10,
            description="Test Description",
        )
        self.url = reverse('bookings:booking_create')
        self.future_time = timezone.now() + timezone.timedelta(days=1)

    def test_view_requires_login(self):
        """Test that the view requires login."""
        response = self.client.get(self.url)
        # Should redirect to login page
        self.assertEqual(response.status_code, 302)

    def test_view_accessible_when_logged_in(self):
        """Test that the view is accessible when logged in."""
        self.client.login(username='testuser', password='password')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)

    def test_view_uses_correct_template(self):
        """Test that the view uses the correct template."""
        self.client.login(username='testuser', password='password')
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'bookings/booking_form.html')

    def test_can_create_booking(self):
        """Test that a booking can be created."""
        self.client.login(username='testuser', password='password')
        data = {
            'facility': self.facility.id,
            'title': 'New Booking',
            'description': 'New Description',
            'start_time': self.future_time.strftime('%Y-%m-%dT%H:%M'),
            'end_time': (self.future_time + timezone.timedelta(hours=2)).strftime('%Y-%m-%dT%H:%M'),
            'number_of_people': 5,
        }
        response = self.client.post(self.url, data)
        # Should redirect to booking list
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse('bookings:booking_list'))
        # Check if booking was created
        self.assertTrue(Booking.objects.filter(title='New Booking').exists())
