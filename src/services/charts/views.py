from django.shortcuts import render
from django.views import View
import openpyxl
from django.http import HttpResponse
from src.services.project.models import Project

class ChartsIndex(View):
    def get(self, request, *args, **kwargs):
        projects = Project.objects.all()
        return render(request, 'charts/charts_index.html', {'projects': projects})


def export_project_to_excel(request, pk):
    project = Project.objects.get(pk=pk)
    invoices = project.invoices.all()
    expenses = project.expenses.all()

    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = f"{project.project_name} Records"

    # Add Headers
    sheet.append(['Project Name', 'Description', 'Customer', 'Status', 'Total Budget'])
    sheet.append([
        project.project_name,
        project.description,
        str(project.customer),  # Convert customer to string
        project.project_status,
        project.get_total_budget()
    ])

    # Invoices
    sheet.append([])
    sheet.append(['Invoices'])
    sheet.append(['Invoice Number', 'Client Name', 'Total Amount', 'Status', 'Date'])
    for invoice in invoices:
        sheet.append([
            invoice.invoice_number,
            invoice.client_name,
            invoice.total_amount,
            invoice.status,
            invoice.date
        ])

    # Expenses
    sheet.append([])
    sheet.append(['Expenses'])
    sheet.append(['Description', 'Amount', 'Source', 'Category', 'Payment Status', 'Vendor'])
    for expense in expenses:
        sheet.append([
            expense.description,
            expense.amount,
            expense.budget_source,
            expense.category.name if expense.category else '',
            expense.payment_status,
            expense.vendor.name if expense.vendor else ''
        ])

    # Trial Balance
    if hasattr(project, 'get_trial_balance'):  # Ensure get_trial_balance exists
        trial_balance = project.get_trial_balance()
        sheet.append([])
        sheet.append(['Trial Balance'])
        for key, value in trial_balance.items():
            sheet.append([key, value])

    # Return as Response
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = f'attachment; filename="{project.project_name}_records.xlsx"'
    workbook.save(response)
    return response
