from django.urls import reverse_lazy
from django.views.generic import TemplateView, CreateView
from .forms import CustomerForm
from .models import Customer


# Create your views here.
class CustomerView(TemplateView):
    template_name = 'customer/customer_index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['customers'] = Customer.objects.all()[:10]
        return context


class CustomerCreateView(CreateView):
    template_name = 'customer/customer_create.html'
    form_class = CustomerForm
    model = Customer
    success_url = reverse_lazy('customer:home')
