from django.contrib import admin
from django.utils.html import format_html
from django_summernote.admin import SummernoteModelAdmin

from .models import Post


@admin.register(Post)
class PostAdmin(SummernoteModelAdmin):
    summernote_fields = ("content",)
    list_display = ("title", "published_date", "is_published", "image_preview", "updated_at")
    list_filter = ("is_published",)
    list_editable = ("is_published",)
    search_fields = ("title", "content")
    date_hierarchy = "published_date"
    save_on_top = True
    prepopulated_fields = {"slug": ("title",)}
    readonly_fields = ("created_at", "updated_at", "image_preview")

    fieldsets = (
        ("Content", {
            "fields": ("title", "slug", "content", "featured_image", "image_preview"),
        }),
        ("Publishing", {
            "fields": ("published_date", "is_published"),
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
        if obj.featured_image:
            return format_html('<img src="{}" style="height:80px; border-radius:4px;">', obj.featured_image.url)
        return "—"
    image_preview.short_description = "Image Preview"
