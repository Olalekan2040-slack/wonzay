from django.contrib import admin
from .models import StaticPage


@admin.register(StaticPage)
class StaticPageAdmin(admin.ModelAdmin):
    list_display = ["title", "slug", "is_active", "updated_at"]
    prepopulated_fields = {"slug": ("title",)}
