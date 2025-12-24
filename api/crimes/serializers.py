from rest_framework import serializers
from .models import SectorCrimeStat, CrimeCategory

class SectorCrimeStatSerializer(serializers.ModelSerializer):
    # displays the category name string instead of the ID
    category = serializers.SlugRelatedField(
        read_only=True,
        slug_field='name'
    )

    class Meta:
        model = SectorCrimeStat
        fields = ['category', 'count']