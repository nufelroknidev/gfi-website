from django.contrib import admin
from django.http import HttpResponseRedirect
from django.urls import reverse

from .models import SiteSettings


@admin.register(SiteSettings)
class SiteSettingsAdmin(admin.ModelAdmin):
    fieldsets = (
        ("Contact Information", {
            "fields": ("phone", "phone_dialable", "email"),
            "description": "These values appear in the top bar and on the contact page.",
        }),
        ("Location", {
            "fields": ("address", "map_url"),
            "description": "Office address shown in the footer. Paste a Google Maps share URL to make it clickable.",
        }),
        ("Social Media", {
            "fields": ("linkedin_url", "facebook_url", "instagram_url", "twitter_url", "youtube_url", "tiktok_url", "whatsapp_url", "line_url", "wechat_id"),
            "description": "Leave a field blank to hide that icon from the website.",
        }),
    )

    def has_add_permission(self, request):
        return not SiteSettings.objects.exists()

    def has_delete_permission(self, request, obj=None):
        return False

    def changelist_view(self, request, extra_context=None):
        obj = SiteSettings.load()
        change_url = reverse("admin:pages_sitesettings_change", args=[obj.pk])
        return HttpResponseRedirect(change_url)
