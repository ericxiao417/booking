"""
URL configuration for the bookings app.
"""
from django.urls import path

from booking.apps.bookings import views

app_name = 'bookings'

urlpatterns = [
    path('', views.BookingListView.as_view(), name='booking_list'),
    path('<int:pk>/', views.BookingDetailView.as_view(), name='booking_detail'),
    path('create/', views.BookingCreateView.as_view(), name='booking_create'),
    path('<int:pk>/update/', views.BookingUpdateView.as_view(), name='booking_update'),
    path('<int:pk>/cancel/', views.BookingCancelView.as_view(), name='booking_cancel'),
    path('<int:pk>/confirm/', views.BookingConfirmView.as_view(), name='booking_confirm'),
    path('<int:pk>/delete/', views.BookingDeleteView.as_view(), name='booking_delete'),
]
