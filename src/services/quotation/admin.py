from django.contrib import admin
from .models import Quotation, QuotationItem


class QuotationItemInline(admin.TabularInline):
    model = QuotationItem
    extra = 1
    fields = ("item_name", "description", "quantity", "rate", "tax", "amount")
    readonly_fields = ("amount",)
    show_change_link = True


@admin.register(Quotation)
class QuotationAdmin(admin.ModelAdmin):
    list_display = (
        "quotation_number",
        "client_name",
        "company_name",
        "total_amount",
        "status",
        "date",
        "project",
    )
    search_fields = (
        "quotation_number",
        "client_name",
        "company_name",
        "project__project_name",
    )
    list_filter = ("date", "letterhead", "tax")
    inlines = [QuotationItemInline]
    readonly_fields = ("quotation_number", "total_in_words", "total_amount")
    ordering = ("-created_at",)

    def status(self, obj):
        return "Tax Included" if obj.tax else "Tax Excluded"


@admin.register(QuotationItem)
class QuotationItemAdmin(admin.ModelAdmin):
    list_display = ("item_name", "quantity", "rate", "tax", "amount", "quotation")
    search_fields = ("item_name", "description", "quotation__quotation_number")
    readonly_fields = ("amount",)
    list_filter = ("quotation__project",)
