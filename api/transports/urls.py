from django.urls import path
from .views import CommuterSearchView

urlpatterns = [
    path('commute/', CommuterSearchView.as_view(), name='commuter-search'),
]