from django.contrib import admin
from django.utils.translation import gettext_lazy as _
from .models import Ledger, Project, ContentType


class LedgerAdmin(admin.ModelAdmin):
    # Define list view fields
    list_display = (
        "transaction_type",
        "project",
        "amount",
        "source",
        "destination",
        "created_at",
    )

    # Define filters for the list view
    list_filter = ("transaction_type", "project", "created_at", "expense_category")

    # Define search fields
    search_fields = (
        "transaction_type",
        "reason",
        "amount",
        "project__name",
        "source__name",
        "destination__name",
    )

    # Define ordering
    ordering = ("-created_at",)

    # Exclude 'source' and 'destination' as these are non-editable
    exclude = ("source", "destination")

    # Display fields for detail view (but exclude 'source' and 'destination')
    fields = (
        "transaction_type",
        "project",
        "amount",
        "source_content_type",
        "source_object_id",
        "destination_content_type",
        "destination_object_id",
        "expense_category",
        "expense",
        "reason",
        "created_at",
    )

    # Prepopulate fields for specific transaction types
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        if obj and obj.transaction_type == "CREATE_EXPENSE":
            form.base_fields["expense_category"].required = True
        return form

    # Display read-only fields for fields like `created_at`
    readonly_fields = ("created_at",)

    # Add custom actions (for example, bulk updates)
    def mark_as_processed(self, request, queryset):
        # Custom action logic for bulk processing
        queryset.update(transaction_type="TRANSFER")
        self.message_user(request, _("Successfully updated the selected ledgers."))

    mark_as_processed.short_description = _("Mark selected transactions as Processed")

    actions = [mark_as_processed]


# Register the Ledger model with the customized admin
admin.site.register(Ledger, LedgerAdmin)
