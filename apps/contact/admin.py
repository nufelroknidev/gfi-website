from django.contrib import admin

from .models import Inquiry


@admin.action(description="Mark selected inquiries as read")
def mark_as_read(modeladmin, request, queryset):
    queryset.update(is_read=True)


@admin.register(Inquiry)
class InquiryAdmin(admin.ModelAdmin):
    actions = [mark_as_read]
    list_display = ("name", "email", "company", "subject", "message_preview", "submitted_at", "is_read")
    list_filter = ("is_read",)
    list_editable = ("is_read",)
    search_fields = ("name", "email", "subject", "message")
    date_hierarchy = "submitted_at"
    readonly_fields = (
        "name", "email", "company", "phone",
        "subject", "message", "product_interest", "submitted_at",
    )

    fieldsets = (
        ("Contact Details", {
            "fields": ("name", "email", "company", "phone"),
        }),
        ("Inquiry", {
            "fields": ("subject", "message", "product_interest"),
        }),
        ("Status", {
            "fields": ("is_read", "submitted_at"),
        }),
    )

    def message_preview(self, obj):
        return obj.message[:80] + "…" if len(obj.message) > 80 else obj.message
    message_preview.short_description = "Message"

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
