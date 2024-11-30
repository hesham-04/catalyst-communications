from src.services.transaction.models import Ledger

from django.core.paginator import Paginator
from django.views import View
from django.shortcuts import render

import openpyxl
from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
from django.http import HttpResponse
from datetime import datetime
from src.services.project.models import Project


class ChartsIndex(View):
    def get(self, request, *args, **kwargs):
        projects = Project.objects.all()

        paginator = Paginator(projects, 10)
        page_number = request.GET.get('page', 1)
        page_obj = paginator.get_page(page_number)

        return render(request, 'charts/charts_index.html', {'page_obj': page_obj})


def export_project_to_excel(request, pk):
    # Retrieve the project by primary key
    project = Project.objects.get(pk=pk)
    invoices = project.invoices.all()
    expenses = project.expenses.all()

    # Create a new workbook and set the title
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = f"{project.project_name} Records"

    # Styles
    title_font = Font(size=14, bold=True, color="FFFFFF")
    header_font = Font(size=12, bold=True, color="FFFFFF")
    normal_font = Font(size=11)
    centered_alignment = Alignment(horizontal="center", vertical="center")
    left_alignment = Alignment(horizontal="left", vertical="center")
    title_fill = PatternFill("solid", fgColor="4F81BD")  # Blue background
    header_fill = PatternFill("solid", fgColor="A9C6E8")  # Light blue background
    thin_border = Border(
        left=Side(style="thin"), right=Side(style="thin"),
        top=Side(style="thin"), bottom=Side(style="thin")
    )
    bold_border = Border(
        left=Side(style="thick"), right=Side(style="thick"),
        top=Side(style="thick"), bottom=Side(style="thick")
    )

    # Header: Project Info Section
    sheet.merge_cells(start_row=1, start_column=1, end_row=1, end_column=5)
    sheet["A1"] = f"{project.project_name} Financial Overview"
    sheet["A1"].font = title_font
    sheet["A1"].alignment = centered_alignment
    sheet["A1"].fill = title_fill

    # Add Project Information as the first section
    project_info_start_row = 3
    sheet.append(['Project Name', 'Description', 'Customer', 'Status', 'Total Budget'])
    sheet.append([
        project.project_name,
        project.description or "N/A",
        str(project.customer),
        project.project_status,
        project.get_total_budget() or 'N/A',  # Handle case where total budget might be None
    ])

    # Apply styles to the project information section
    for row in sheet.iter_rows(min_row=project_info_start_row, max_row=project_info_start_row + 1, min_col=1, max_col=5):
        for cell in row:
            cell.font = normal_font
            cell.alignment = left_alignment
            cell.border = thin_border

    # Add a blank line for separation
    sheet.append([])

    # Add Invoices Section
    sheet.append(['Invoices'])
    sheet.append(['Invoice Number', 'Client Name', 'Total Amount', 'Status', 'Date'])
    for invoice in invoices:
        sheet.append([
            invoice.invoice_number,
            invoice.client_name,
            invoice.total_amount,
            invoice.status,
            invoice.date.strftime('%Y-%m-%d') if invoice.date else '',
        ])

    # Apply styling to invoices
    for row in sheet.iter_rows(min_row=project_info_start_row + 4, max_row=project_info_start_row + 4 + len(invoices), min_col=1, max_col=5):
        for cell in row:
            cell.font = normal_font
            cell.alignment = left_alignment
            cell.border = thin_border

    # Add a blank line for separation
    sheet.append([])

    # Add Expenses Section
    sheet.append(['Expenses'])
    sheet.append(['Description', 'Amount', 'Source', 'Category', 'Payment Status', 'Vendor'])
    for expense in expenses:
        sheet.append([
            expense.description,
            expense.amount,
            expense.budget_source,
            expense.category.name if expense.category else 'N/A',
            expense.payment_status,
            expense.vendor.name if expense.vendor else 'N/A'
        ])

    # Apply styling to expenses
    for row in sheet.iter_rows(min_row=project_info_start_row + 6 + len(invoices), max_row=project_info_start_row + 6 + len(invoices) + len(expenses), min_col=1, max_col=6):
        for cell in row:
            cell.font = normal_font
            cell.alignment = left_alignment
            cell.border = thin_border

    # Add a blank line for separation
    sheet.append([])

    # Add Trial Balance Section if it exists
    if hasattr(project, 'get_trial_balance'):  # Ensure get_trial_balance exists
        trial_balance = project.get_trial_balance()
        sheet.append(['Trial Balance'])
        for key, value in trial_balance.items():
            sheet.append([key, value])

        # Apply styling to trial balance section
        for row in sheet.iter_rows(min_row=project_info_start_row + 8 + len(invoices) + len(expenses), max_row=project_info_start_row + 8 + len(invoices) + len(expenses) + len(trial_balance), min_col=1, max_col=2):
            for cell in row:
                cell.font = normal_font
                cell.alignment = left_alignment
                cell.border = thin_border

    # Adjust column widths to fit content
    sheet.column_dimensions["A"].width = 30
    sheet.column_dimensions["B"].width = 40
    sheet.column_dimensions["C"].width = 25
    sheet.column_dimensions["D"].width = 20
    sheet.column_dimensions["E"].width = 20
    sheet.column_dimensions["F"].width = 25

    # Return the Excel file as a response
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{project.project_name}_records.xlsx"'

    # Save the workbook to the response object
    workbook.save(response)

    return response


def generate_monthly_report(request, month, year):
    from openpyxl import Workbook
    from openpyxl.styles import Font, Alignment, PatternFill, Border, Side
    from django.http import HttpResponse
    from datetime import datetime
    from src.services.project.models import Project

    # Fetch all projects created in the specified month and year
    projects = Project.objects.filter(created_at__year=year, created_at__month=month)

    # Create Excel workbook and sheet
    workbook = Workbook()
    sheet = workbook.active
    sheet.title = f"Monthly Report - {month}-{year}"

    # Styles
    title_font = Font(size=14, bold=True, color="FFFFFF")
    header_font = Font(size=12, bold=True)
    normal_font = Font(size=11)
    centered_alignment = Alignment(horizontal="center", vertical="center")
    left_alignment = Alignment(horizontal="left", vertical="center")
    title_fill = PatternFill("solid", fgColor="4F81BD")  # Blue background
    header_fill = PatternFill("solid", fgColor="D9E1F2")  # Light blue
    thin_border = Border(
        left=Side(style="thin"), right=Side(style="thin"),
        top=Side(style="thin"), bottom=Side(style="thin")
    )

    # Header: Catalyst Communications Monthly Report
    sheet.merge_cells(start_row=1, start_column=1, end_row=1, end_column=len(projects) * 5)
    sheet["A1"] = f"Catalyst Communications - Monthly Financial Report ({month}/{year})"
    sheet["A1"].font = title_font
    sheet["A1"].alignment = centered_alignment
    sheet["A1"].fill = title_fill

    # Loop through each project and add its data side by side
    start_col = 1
    col_width = 5  # Number of columns per project
    for project in projects:
        # Project header row
        col_letter = lambda col: openpyxl.utils.get_column_letter(col)
        project_title_cell = f"{col_letter(start_col)}2"
        sheet.merge_cells(start_row=2, start_column=start_col, end_row=2, end_column=start_col + col_width - 1)
        sheet[project_title_cell] = f"Project: {project.project_name}"
        sheet[project_title_cell].font = header_font
        sheet[project_title_cell].alignment = centered_alignment
        sheet[project_title_cell].fill = header_fill

        # Project details
        details_start_row = 3
        sheet[f"{col_letter(start_col)}{details_start_row}"] = "Description"
        sheet[f"{col_letter(start_col + 1)}{details_start_row}"] = "Customer"
        sheet[f"{col_letter(start_col + 2)}{details_start_row}"] = "Status"
        sheet[f"{col_letter(start_col + 3)}{details_start_row}"] = "Cash"
        sheet[f"{col_letter(start_col + 4)}{details_start_row}"] = "Account"

        project_values = [
            project.description or "N/A",
            str(project.customer),
            project.get_project_status_display(),
            project.project_cash,
            project.project_account_balance,
        ]
        for idx, value in enumerate(project_values):
            cell = f"{col_letter(start_col + idx)}{details_start_row + 1}"
            sheet[cell] = value
            sheet[cell].font = normal_font
            sheet[cell].alignment = left_alignment
            sheet[cell].border = thin_border

        # Invoices section
        invoices_start_row = details_start_row + 3
        sheet[f"{col_letter(start_col)}{invoices_start_row}"] = "Invoices"
        sheet[f"{col_letter(start_col)}{invoices_start_row}"].font = header_font
        sheet[f"{col_letter(start_col)}{invoices_start_row}"].alignment = centered_alignment

        invoices = project.invoices.all()  # Assuming related_name='invoices'
        if invoices.exists():
            for invoice in invoices:
                sheet[f"{col_letter(start_col)}{invoices_start_row + 1}"] = invoice.invoice_number
                sheet[f"{col_letter(start_col + 1)}{invoices_start_row + 1}"] = invoice.client_name
                sheet[f"{col_letter(start_col + 2)}{invoices_start_row + 1}"] = invoice.total_amount
                invoices_start_row += 1
        else:
            sheet[f"{col_letter(start_col)}{invoices_start_row + 1}"] = "No invoices available"

        # Expenses section
        expenses_start_row = invoices_start_row + 3
        sheet[f"{col_letter(start_col)}{expenses_start_row}"] = "Expenses"
        sheet[f"{col_letter(start_col)}{expenses_start_row}"].font = header_font
        sheet[f"{col_letter(start_col)}{expenses_start_row}"].alignment = centered_alignment

        expenses = project.expenses.all()  # Assuming related_name='expenses'
        if expenses.exists():
            for expense in expenses:
                sheet[f"{col_letter(start_col)}{expenses_start_row + 1}"] = expense.description
                sheet[f"{col_letter(start_col + 1)}{expenses_start_row + 1}"] = expense.amount
                sheet[f"{col_letter(start_col + 2)}{expenses_start_row + 1}"] = expense.budget_source
                expenses_start_row += 1
        else:
            sheet[f"{col_letter(start_col)}{expenses_start_row + 1}"] = "No expenses available"

        # Trial balance section
        trial_start_row = expenses_start_row + 3
        sheet[f"{col_letter(start_col)}{trial_start_row}"] = "Trial Balance"
        sheet[f"{col_letter(start_col)}{trial_start_row}"].font = header_font
        sheet[f"{col_letter(start_col)}{trial_start_row}"].alignment = centered_alignment

        if hasattr(project, 'get_trial_balance'):
            trial_balance = project.get_trial_balance()
            for key, value in trial_balance.items():
                sheet[f"{col_letter(start_col)}{trial_start_row + 1}"] = key
                sheet[f"{col_letter(start_col + 1)}{trial_start_row + 1}"] = value
                trial_start_row += 1

        # Move to next project's columns
        start_col += col_width

    # Adjust column widths
    for col in range(1, start_col):
        sheet.column_dimensions[openpyxl.utils.get_column_letter(col)].width = 20

    # Return the Excel file as HTTP response
    response = HttpResponse(content_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    response['Content-Disposition'] = f'attachment; filename="monthly_report_{month}_{year}.xlsx"'
    workbook.save(response)
    return response


def download_journal(request, pk):
    # Retrieve the project by primary key
    project = Project.objects.get(pk=pk)

    # Fetch all the ledger entries related to this project
    ledger_entries = Ledger.objects.filter(project=project)

    # Create a new workbook and set the title
    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.title = f"{project.project_name} Ledger Journal"

    # Styles
    header_font = Font(size=12, bold=True, color="FFFFFF")
    normal_font = Font(size=11)
    centered_alignment = Alignment(horizontal="center", vertical="center")
    left_alignment = Alignment(horizontal="left", vertical="center")
    header_fill = PatternFill("solid", fgColor="4F81BD")  # Blue background for headers
    thin_border = Border(
        left=Side(style="thin"), right=Side(style="thin"),
        top=Side(style="thin"), bottom=Side(style="thin")
    )

    # Add a title row with project information
    sheet.merge_cells(start_row=1, start_column=1, end_row=1, end_column=5)
    sheet["A1"] = f"Ledger Journal for {project.project_name}"
    sheet["A1"].font = Font(size=14, bold=True, color="FFFFFF")
    sheet["A1"].alignment = centered_alignment
    sheet["A1"].fill = header_fill

    # Add Column Headers
    sheet.append(['Transaction Type', 'Amount', 'Source', 'Destination', 'Reason', 'Date'])

    # Apply header styles
    for cell in sheet[2]:
        cell.font = header_font
        cell.alignment = centered_alignment
        cell.fill = header_fill
        cell.border = thin_border

    # Add Ledger Entries
    for ledger in ledger_entries:
        sheet.append([
            ledger.get_transaction_type_display(),  # Human-readable transaction type
            ledger.amount,
            ledger.source,
            ledger.destination,
            ledger.reason if ledger.reason else 'N/A',  # Handle missing reason
            ledger.created_at.strftime('%Y-%m-%d %H:%M:%S')  # Format the date
        ])

    # Apply normal cell styles for the data rows
    for row in sheet.iter_rows(min_row=3, max_row=3 + len(ledger_entries), min_col=1, max_col=6):
        for cell in row:
            cell.font = normal_font
            cell.alignment = left_alignment if cell.column != 2 else centered_alignment  # Amount is centered
            cell.border = thin_border

    # Adjust column widths
    sheet.column_dimensions["A"].width = 20
    sheet.column_dimensions["B"].width = 15
    sheet.column_dimensions["C"].width = 25
    sheet.column_dimensions["D"].width = 25
    sheet.column_dimensions["E"].width = 30
    sheet.column_dimensions["F"].width = 20

    # Return the Excel file as a response
    response = HttpResponse(
        content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet'
    )
    response['Content-Disposition'] = f'attachment; filename="{project.project_name}_ledger_journal.xlsx"'

    # Save the workbook to the response object
    workbook.save(response)

    return response