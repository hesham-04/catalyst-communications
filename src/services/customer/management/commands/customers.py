# File: your_app/management/commands/import_customers.py

import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction
from src.services.customer.models import Customer  # Replace with your actual app name

class Command(BaseCommand):
    help = 'Import Customer data from an Excel file into the database'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the Excel file containing data')

    def handle(self, *args, **options):
        file_path = options['file_path']

        try:
            # Read the Excel file
            df = pd.read_excel(file_path, sheet_name='Customer')

            # Replace NaN values with appropriate defaults
            df.fillna({
                'Salutation': "Mr.",
                'First Name': "No Name",
                'Last Name': "No Name",
                'Company Name': "Unknown",
                'Customer Type': "business",
                'Currency': "PKR",
                'Payment Due Period': "due_on_recipt",
                'Company ID': "COMP000"
            }, inplace=True)

            # Start a transaction
            with transaction.atomic():
                for index, row in df.iterrows():
                    try:
                        # Preprocess data
                        salutation = str(row.get('Salutation', "Mr.")).strip()
                        first_name = str(row.get('First Name', "No Name")).strip()
                        last_name = str(row.get('Last Name', "No Name")).strip()
                        company_name = str(row.get('Company Name', "Unknown")).strip()
                        customer_type = str(row.get('Customer Type', '')).lower()
                        currency = str(row.get('Currency', 'PKR')).upper()
                        payment_due_period = str(row.get('Payment Due Period', '')).lower().replace(" ", "_")
                        company_id = str(row.get('Company ID', '')).strip()

                        # Map customer type and payment due period to model choices
                        customer_type_map = {
                            "govt dept": "business",
                            "social sector": "business",
                            "company": "business",
                        }
                        customer_type = customer_type_map.get(customer_type, "business")

                        payment_due_period_map = {
                            "due_on_recipt": "due_receipt",
                            "net_15": "net_15",
                            "net_45": "net_45",
                            "net_60": "net_60",
                            "due_end_of_month": "due_eom",
                        }
                        payment_due_period = payment_due_period_map.get(payment_due_period, "due_eom")

                        # Generate a unique company ID if not provided
                        if not company_id or company_id == "COMP000":
                            company_id = f"COMP{index + 1:03}"

                        # Create or update the Customer instance
                        customer, created = Customer.objects.update_or_create(
                            company_id=company_id,
                            defaults={
                                'salutation': salutation,
                                'first_name': first_name,
                                'last_name': last_name,
                                'company_name': company_name,
                                'customer_type': customer_type,
                                'currency': currency,
                                'payment_due_period': payment_due_period,
                            }
                        )

                        self.stdout.write(self.style.SUCCESS(f"Processed customer: {first_name} {last_name}"))

                    except Exception as e:
                        self.stderr.write(self.style.ERROR(f"Error processing row {index + 1}: {e}"))
                        raise  # Re-raise the exception to trigger a rollback

            self.stdout.write(self.style.SUCCESS("Data imported successfully!"))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error importing data: {e}"))