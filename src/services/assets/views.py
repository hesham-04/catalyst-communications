from django.shortcuts import render
from django.urls import reverse_lazy
from django.views.generic.edit import CreateView, UpdateView, DeleteView
from django.views import View
from .models import CashInHand, AccountBalance
from django.db.models import Sum
from django.views.generic import TemplateView, UpdateView, ListView



class IndexView(TemplateView):
    template_name = 'assets/assets_index.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        cash_in_hand = CashInHand.objects.first()
        context['cash_in_hand'] = cash_in_hand.balance if cash_in_hand else 0


        account_balance = AccountBalance.objects.aggregate(total_balance=Sum('balance'))['total_balance']
        accounts = AccountBalance.objects.count()
        context['account_balance'] = account_balance if account_balance else 0
        context['accounts'] = accounts if accounts else 0

        return context


class CashInHandIndexView(View):
    def get(self, request, *args, **kwargs):
        cashinhand = CashInHand.objects.first() or 0

        context ={
            'cashinhand': cashinhand,
        }

        return render(request, 'assets/cashinhand_list.html', context)



# CashInHand Views
class CashInHandCreateView(CreateView):
    model = CashInHand
    fields = ['name', 'balance']
    template_name = 'cashinhand_form.html'
    success_url = reverse_lazy('cashinhand_list')

class CashInHandUpdateView(UpdateView):
    model = CashInHand
    fields = ['name', 'balance']
    template_name = 'cashinhand_form.html'
    success_url = reverse_lazy('cashinhand_list')

class CashInHandDeleteView(DeleteView):
    model = CashInHand
    template_name = 'cashinhand_confirm_delete.html'
    success_url = reverse_lazy('cashinhand_list')




class AccountBalanceCreateView(CreateView):
    model = AccountBalance
    fields = ['account_name', 'balance']
    success_url = reverse_lazy('assets:accounts')

class AccountBalanceList(ListView):
    model = AccountBalance

class AccountBalanceUpdateView(UpdateView):
    model = AccountBalance
    fields = ['account_name', 'balance']
    success_url = reverse_lazy('assets:accounts')

class AccountBalanceDeleteView(DeleteView):
    model = AccountBalance
    template_name = 'accountbalance_confirm_delete.html'
    success_url = reverse_lazy('assets:accounts')
