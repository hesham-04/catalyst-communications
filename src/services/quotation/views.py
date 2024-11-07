from django.shortcuts import render
from django.views.generic import TemplateView

# Create your views here.
class QuotaionView(TemplateView):
    template_name = 'quotation/quotation_index.html'