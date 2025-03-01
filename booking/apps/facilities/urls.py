"""
URL configuration for the facilities app.
"""
from django.urls import path

from booking.apps.facilities import views

app_name = 'facilities'

urlpatterns = [
    path('', views.FacilityListView.as_view(), name='facility_list'),
    path('<int:pk>/', views.FacilityDetailView.as_view(), name='facility_detail'),
    path('create/', views.FacilityCreateView.as_view(), name='facility_create'),
    path('<int:pk>/update/', views.FacilityUpdateView.as_view(), name='facility_update'),
    path('<int:pk>/delete/', views.FacilityDeleteView.as_view(), name='facility_delete'),
]
