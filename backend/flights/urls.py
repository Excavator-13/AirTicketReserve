from django.urls import path

from flights.views import CityListView, FlightSearchView, FlightDetailView

urlpatterns = [
    path('flights/cities/', CityListView.as_view(), name='city-list'),
    path('flights/search/', FlightSearchView.as_view(), name='flight-search'),
    path('flights/<uuid:pk>/', FlightDetailView.as_view(), name='flight-detail'),
]