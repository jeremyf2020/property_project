from rest_framework import viewsets
from .models import School
from .serializers import SchoolSerializer

class SchoolViewSet(viewsets.ReadOnlyModelViewSet):
    # Order by name so the list is readable in Swagger
    queryset = School.objects.all().order_by('name')
    serializer_class = SchoolSerializer