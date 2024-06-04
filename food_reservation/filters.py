from django_filters import rest_framework as filters, NumberFilter
from django.db.models import Avg
from .models import Organization,Food

class OrganizationFilter(filters.FilterSet):
    average_rate_gte = NumberFilter(field_name='average_rate', lookup_expr='gte')
    average_rate_lte = NumberFilter(field_name='average_rate', lookup_expr='lte')

    class Meta:
        model = Organization
        fields = {
            'name': ['icontains'],
        }

    def filter_by_average_rate(self, queryset, name, value):
        return queryset.annotate(average_rate=Avg('buffets__rates__rate')).filter(average_rate=value)

    def get_queryset(self):
        return super().get_queryset().annotate(average_rate=Avg('buffets__rates__rate'))
    
    
class FoodFilter(filters.FilterSet):
    class Meta:
        model = Food
        fields = {
            'name': ['icontains'],
        }
