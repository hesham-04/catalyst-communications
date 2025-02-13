# File: your_app/management/commands/import_lenders.py

import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction
from src.services.loan.models import Lender  # Replace with your actual app name

class Command(BaseCommand):
    help = 'Import Lender data from an Excel file into the database'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the Excel file containing data')

    def handle(self, *args, **options):
        file_path = options['file_path']

        try:
            # Read the Excel file
            df = pd.read_excel(file_path, sheet_name='Lender')

            # Replace NaN values with appropriate defaults
            df.fillna({
                'Name': "Unknown Lender",
                'Email': "",
                'Phone': "",
                'Bank Account': "",
                'Account Number': "",
                'IBAN': ""
            }, inplace=True)

            # Start a transaction
            with transaction.atomic():
                for index, row in df.iterrows():
                    try:
                        # Preprocess data
                        name = str(row.get('Name', '')).strip() or "Unknown Lender"
                        email = str(row.get('Email', '')).strip() or None
                        phone = str(row.get('Phone', '')).strip() or None
                        bank_account = str(row.get('Bank Account', '')).strip() or None
                        account_number = str(row.get('Account Number', '')).strip() or None
                        iban = str(row.get('IBAN', '')).strip() or None

                        # Create or update the Lender instance
                        lender, created = Lender.objects.update_or_create(
                            name=name,
                            defaults={
                                'email': email,
                                'phone': phone,
                                'bank_account': bank_account,
                                'account_number': account_number,
                                'iban': iban,
                            }
                        )

                        self.stdout.write(self.style.SUCCESS(f"Processed lender: {name}"))

                    except Exception as e:
                        self.stderr.write(self.style.ERROR(f"Error processing row {index + 1}: {e}"))
                        raise  # Re-raise the exception to trigger a rollback

            self.stdout.write(self.style.SUCCESS("Data imported successfully!"))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error importing data: {e}"))