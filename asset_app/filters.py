from django.contrib.auth.models import User
import django_filters
from .models import Component

class ComponentFilter(django_filters.FilterSet):
    class Meta:
        model = Component
        fields = ['name']

