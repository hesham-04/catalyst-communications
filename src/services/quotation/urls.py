from django.urls import path
from . views import QuotaionView

app_name = 'quotation'

urlpatterns = [
    path('', QuotaionView.as_view(), name='index'),
]