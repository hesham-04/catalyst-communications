from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import TemplateView, CreateView, DetailView, UpdateView

from src.core.forms import BillingAddressForm, ShippingAddressForm
from src.core.models import Customer, ShippingAddress, BillingAddress
from .forms import CustomerForm


# Create your views here.
class CustomerView(TemplateView):
    template_name = 'customer/customer_index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['customers'] = Customer.objects.all()[:10]
        return context


class CustomerCreateView(CreateView):
    template_name = 'customer/customer_form.html'
    form_class = CustomerForm
    model = Customer
    success_url = reverse_lazy('customer:index')


class CustomerDetailView(DetailView):
    model = Customer
    template_name = 'customer/customer_detail.html'


class ShippingAddressAddView(CreateView):
    template_name = 'customer/address_form.html'
    model = ShippingAddress
    form_class = ShippingAddressForm
    success_url = reverse_lazy('customer:home')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['customer'] = get_object_or_404(Customer, pk=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        customer = get_object_or_404(Customer, pk=self.kwargs['pk'])

        shipping_address = form.save(commit=False)
        shipping_address.customer = customer
        shipping_address.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('customer:detail', kwargs={'pk': self.object.customer.pk})


class ShippingAddressUpdateView(UpdateView):
    template_name = 'customer/address_form.html'
    form_class = ShippingAddressForm
    model = ShippingAddress

    def get_object(self, queryset=None):
        return get_object_or_404(ShippingAddress, customer_id=self.kwargs['pk'])

    def get_success_url(self):
        return reverse('customer:detail', kwargs={'pk': self.object.customer.pk})


class BillingAddressAddView(CreateView):
    template_name = 'customer/address_form.html'
    model = BillingAddress
    success_url = reverse_lazy('customer:home')
    form_class = BillingAddressForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['customer'] = get_object_or_404(Customer, pk=self.kwargs['pk'])
        return context

    def form_valid(self, form):
        customer = get_object_or_404(Customer, pk=self.kwargs['pk'])

        shipping_address = form.save(commit=False)
        shipping_address.customer = customer
        shipping_address.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('customer:detail', kwargs={'pk': self.object.customer.pk})


class BillingAddressUpdateView(UpdateView):
    template_name = 'customer/address_form.html'
    form_class = BillingAddressForm
    model = BillingAddress

    def get_object(self, queryset=None):
        return get_object_or_404(BillingAddress, customer_id=self.kwargs['pk'])

    def get_success_url(self):
        return reverse('customer:detail', kwargs={'pk': self.object.customer.pk})
