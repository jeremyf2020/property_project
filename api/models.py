from django.db import models

# Create your models here.
from api.coordinates.models import Coordinates
from api.crimes.models import CrimeCategory, SectorCrimeStat
from api.houses.models import HouseFeatures, Address, HouseSale