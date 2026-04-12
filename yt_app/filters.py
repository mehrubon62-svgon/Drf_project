from .models import * 
from django_filters import rest_framework 

class VideoFilter(rest_framework.FilterSet):
    date_from = rest_framework.DateFilter(field_name='created_at', lookup_expr='gte')
    date_to = rest_framework.DateFilter(field_name='created_at', lookup_expr='lte')

    class Meta:
        model = Video
        fields = ['date_from', 'date_to']