# File: your_app/management/commands/import_invoices.py

import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction
from decimal import Decimal
from src.services.invoice.models import Invoice, InvoiceItem
from src.services.project.models import Project
class Command(BaseCommand):
    help = 'Import Invoice data from an Excel file into the database'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the Excel file containing data')

    def handle(self, *args, **options):
        file_path = options['file_path']

        try:
            # Read the Excel file
            df = pd.read_excel(file_path, sheet_name='Invoice')

            # Start a transaction
            with transaction.atomic():
                for index, row in df.iterrows():
                    try:
                        # Preprocess data
                        project_id = int(row.get('Project ID', 0))
                        total_amount = float(row.get('Total Amount', 0))
                        payment_status = str(row.get('Payment Status', '')).upper()
                        invoice_date = pd.to_datetime(row.get('Invoice Date'))
                        due_date = pd.to_datetime(row.get('Due Date'))
                        invoice_id_str = str(row.get('Invoice ID', '')).strip()
                        items_data = str(row.get('Item 1/price/quantity', '')).strip()

                        # Fetch the related Project
                        try:
                            project = Project.objects.get(pk=project_id)
                        except Project.DoesNotExist:
                            self.stderr.write(self.style.WARNING(f"Project with ID {project_id} does not exist. Skipping row {index + 1}."))
                            continue

                        # Map payment status to model choices
                        status_map = {
                            "PAID": "PAID",
                            "PENDING": "PENDING",
                        }
                        payment_status = status_map.get(payment_status, "PENDING")

                        # Create the Invoice instance
                        invoice = Invoice.objects.create(
                            date=invoice_date,
                            client_name=project.customer.first_name or "Unknown",
                            company_name=project.customer.company_name or "Unknown",
                            phone=project.customer.mobile or "00000000000",
                            address="Unknown Address",  # Placeholder, can be updated later
                            email=project.customer.email or "unknown@example.com",
                            subject=f"Invoice for {project.project_name}",
                            notes="Generated via data import script.",
                            total_amount=total_amount,
                            total_in_words="Zero Rupees Only",  # Placeholder, will be updated
                            status=payment_status,
                            due_date=due_date,
                            project=project,
                        )

                        # Update invoice number
                        invoice.invoice_number = f"{invoice_id_str}"
                        invoice.save(update_fields=["invoice_number"])

                        # Parse and create InvoiceItems
                        if items_data:
                            items = items_data.split("/")
                            item_name = items[0].strip()
                            total_price = float(items[1].replace(",", ""))
                            quantity = int(items[2])

                            # Calculate individual item price
                            rate = Decimal(total_price / quantity)

                            # Create the InvoiceItem
                            InvoiceItem.objects.create(
                                invoice=invoice,
                                item_name=item_name,
                                quantity=quantity,
                                rate=rate,
                                tax=Decimal("0.00"),  # Assuming no tax for simplicity
                            )

                        # Recalculate total amount and total in words
                        invoice.calculate_total_amount()

                        self.stdout.write(self.style.SUCCESS(f"Processed invoice: {invoice.invoice_number}"))

                    except Exception as e:
                        self.stderr.write(self.style.ERROR(f"Error processing row {index + 1}: {e}"))
                        raise  # Re-raise the exception to trigger a rollback

            self.stdout.write(self.style.SUCCESS("Data imported successfully!"))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error importing data: {e}"))