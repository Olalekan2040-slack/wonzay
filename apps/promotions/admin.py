from django.contrib import admin
from .models import Coupon, CouponUsage


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ["code", "discount_type", "discount_value", "is_active", "valid_from", "valid_until", "total_uses"]
    list_editable = ["is_active"]
    search_fields = ["code"]
