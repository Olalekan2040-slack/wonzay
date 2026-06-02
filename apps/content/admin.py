from django.contrib import admin
from .models import AnnouncementBar, HeroSlide, TrustBadge, BrandStory


@admin.register(AnnouncementBar)
class AnnouncementBarAdmin(admin.ModelAdmin):
    list_display = ["message", "coupon_code", "is_active", "order"]
    list_editable = ["is_active", "order"]


@admin.register(HeroSlide)
class HeroSlideAdmin(admin.ModelAdmin):
    list_display = ["headline", "is_active", "order"]
    list_editable = ["is_active", "order"]


@admin.register(TrustBadge)
class TrustBadgeAdmin(admin.ModelAdmin):
    list_display = ["label", "is_active", "order"]
    list_editable = ["is_active", "order"]


@admin.register(BrandStory)
class BrandStoryAdmin(admin.ModelAdmin):
    pass
