# File: your_app/management/commands/import_projects.py

import pandas as pd
from django.core.management.base import BaseCommand
from django.db import transaction
from src.services.project.models import Project  # Replace with your actual app name
from src.services.customer.models import Customer  # Assuming Customer model exists in another app

class Command(BaseCommand):
    help = 'Import Project data from an Excel file into the database'

    def add_arguments(self, parser):
        parser.add_argument('file_path', type=str, help='Path to the Excel file containing data')

    def handle(self, *args, **options):
        file_path = options['file_path']

        try:
            # Read the Excel file
            df = pd.read_excel(file_path, sheet_name='Project')

            # Start a transaction
            with transaction.atomic():
                for index, row in df.iterrows():
                    try:
                        # Preprocess data
                        project_name = str(row.get('Project Name', '')).strip() or "Unnamed Project"
                        description = str(row.get('Description', '')).strip() or None
                        customer_id = int(row.get('Customer ID', 0)) if pd.notna(row.get('Customer ID')) else None
                        project_cash = float(row.get('Project Cash', 0))
                        budget_source = str(row.get('Budget Source', '')).upper()
                        created_at = pd.to_datetime(row.get('Created At'))
                        updated_at = pd.to_datetime(row.get('Updated At'))

                        # Override project status to be "In Progress"
                        project_status = "IP"

                        # Map budget source to model choices
                        source_map = {
                            "ACCOUNT": "ACC",
                            "CASH IN HAND": "CASH"
                        }
                        budget_source = source_map.get(budget_source, "CASH")

                        # Fetch the related Customer, skip if not found
                        if customer_id:
                            try:
                                customer = Customer.objects.get(pk=customer_id)
                            except Customer.DoesNotExist:
                                self.stderr.write(self.style.WARNING(f"Customer with ID {customer_id} does not exist. Skipping row {index + 1}."))
                                continue
                        else:
                            customer = None

                        # Create or update the Project instance
                        project, created = Project.objects.update_or_create(
                            project_name=project_name,
                            defaults={
                                'description': description,
                                'customer': customer,
                                'project_cash': project_cash,
                                'project_status': project_status,
                                'budget_source': budget_source,
                                'created_at': created_at,
                                'updated_at': updated_at,
                            }
                        )

                        self.stdout.write(self.style.SUCCESS(f"Processed project: {project_name}"))

                    except Exception as e:
                        self.stderr.write(self.style.ERROR(f"Error processing row {index + 1}: {e}"))

            self.stdout.write(self.style.SUCCESS("Data imported successfully!"))

        except Exception as e:
            self.stderr.write(self.style.ERROR(f"Error importing data: {e}"))