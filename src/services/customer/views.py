from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import (
    TemplateView,
    CreateView,
    DetailView,
    UpdateView,
    DeleteView,
)

from src.core.forms import BillingAddressForm
from src.core.models import Customer, BillingAddress
from .forms import CustomerForm


class CustomerView(LoginRequiredMixin, TemplateView):
    template_name = "customer/customer_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        search_query = self.request.GET.get("q", "")
        customers = Customer.objects.all().order_by("-created_at")

        if search_query:
            customers = customers.filter(
                Q(first_name__icontains=search_query)
                | Q(last_name__icontains=search_query)
                | Q(email__icontains=search_query)
            )

        paginator = Paginator(customers, 10)
        page = self.request.GET.get("page")
        context["customers"] = paginator.get_page(page)

        context["search_query"] = search_query
        return context


class CustomerUpdateView(LoginRequiredMixin, UpdateView):
    model = Customer
    form_class = CustomerForm
    success_url = reverse_lazy("customer:index")


class CustomerDeleteView(LoginRequiredMixin, DeleteView):
    model = Customer
    success_url = reverse_lazy("customer:index")


class CustomerCreateView(LoginRequiredMixin, CreateView):
    template_name = "customer/customer_form.html"
    form_class = CustomerForm
    model = Customer
    success_url = reverse_lazy("customer:index")


class CustomerDetailView(LoginRequiredMixin, DetailView):
    model = Customer
    template_name = "customer/customer_detail.html"


class BillingAddressAddView(LoginRequiredMixin, CreateView):
    template_name = "customer/address_form.html"
    model = BillingAddress
    success_url = reverse_lazy("customer:home")
    form_class = BillingAddressForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["customer"] = get_object_or_404(Customer, pk=self.kwargs["pk"])
        return context

    def form_valid(self, form):
        customer = get_object_or_404(Customer, pk=self.kwargs["pk"])

        shipping_address = form.save(commit=False)
        shipping_address.customer = customer
        shipping_address.save()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse("customer:detail", kwargs={"pk": self.object.customer.pk})


class BillingAddressUpdateView(LoginRequiredMixin, UpdateView):
    template_name = "customer/address_form.html"
    form_class = BillingAddressForm
    model = BillingAddress

    def get_object(self, queryset=None):
        return get_object_or_404(BillingAddress, customer_id=self.kwargs["pk"])

    def get_success_url(self):
        return reverse("customer:detail", kwargs={"pk": self.object.customer.pk})
