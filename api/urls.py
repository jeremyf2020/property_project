from django.urls import path, include
from rest_framework.routers import DefaultRouter
from api.coordinates.views import CoordinatesViewSet
# from api.crimes.views import CrimeViewSet
from api.houses.views import HouseSaleViewSet
from api.schools.views import SchoolViewSet

router = DefaultRouter()
router.register(r'postcode-sector', CoordinatesViewSet, basename='coordinates')
router.register(r'house-sales', HouseSaleViewSet, basename='house-sale')
# router.register(r'crimes', CrimeViewSet)
router.register(r'schools', SchoolViewSet, basename='school')

urlpatterns = [
    path('', include(router.urls)),
    path('transports/', include('api.transports.urls')),
]