from django.contrib import admin
from django.db.models import Count
from django.utils.html import format_html

from .models import Application, Category, Certification, Product


@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "order")
    list_editable = ("order",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ("name", "slug", "order")
    list_editable = ("order",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "order", "product_count", "image_preview")
    list_editable = ("order",)
    search_fields = ("name",)
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("image_preview",)

    def get_queryset(self, request):
        return super().get_queryset(request).annotate(_product_count=Count("products"))

    def product_count(self, obj):
        return obj._product_count
    product_count.short_description = "Products"
    product_count.admin_order_field = "_product_count"

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:40px; border-radius:4px;">', obj.image.url)
        return "—"
    image_preview.short_description = "Image"


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ("name", "category", "origin", "is_active", "has_datasheet", "image_preview", "updated_at")
    list_filter = ("category", "is_active", "origin", "certifications", "applications")
    search_fields = ("name", "cas_number", "e_number", "alternative_names", "description")
    list_editable = ("is_active",)
    list_select_related = ("category",)
    save_on_top = True
    prepopulated_fields = {"slug": ("name",)}
    readonly_fields = ("created_at", "updated_at", "image_preview")
    filter_horizontal = ("certifications", "applications")

    fieldsets = (
        ("Basic Info", {
            "fields": ("category", "name", "slug", "is_active"),
        }),
        ("Identification", {
            "description": "These fields are indexed for search. CAS numbers are commonly used by B2B buyers.",
            "fields": ("cas_number", "e_number", "alternative_names"),
        }),
        ("Content", {
            "fields": ("description", "specifications"),
        }),
        ("Classification", {
            "fields": ("origin", "available_forms", "certifications", "applications"),
        }),
        ("Media", {
            "fields": ("image", "image_preview", "datasheet"),
        }),
        ("SEO", {
            "classes": ("collapse",),
            "fields": ("meta_title", "meta_description"),
        }),
        ("Timestamps", {
            "classes": ("collapse",),
            "fields": ("created_at", "updated_at"),
        }),
    )

    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" style="height:80px; border-radius:4px;">', obj.image.url)
        return "—"
    image_preview.short_description = "Image Preview"

    def has_datasheet(self, obj):
        return bool(obj.datasheet)
    has_datasheet.boolean = True
    has_datasheet.short_description = "TDS"
