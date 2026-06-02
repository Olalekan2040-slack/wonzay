from django.contrib import admin
from .models import Order, OrderItem, ShippingRate, ShippingAddress


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ["product_name", "variant_label", "unit_price", "quantity", "line_total"]


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ["order_number", "customer", "total", "status", "payment_status", "created_at"]
    list_filter = ["status", "payment_status"]
    search_fields = ["order_number", "guest_email"]
    inlines = [OrderItemInline]
    readonly_fields = ["order_number", "created_at"]


@admin.register(ShippingRate)
class ShippingRateAdmin(admin.ModelAdmin):
    list_display = ["name", "country_code", "rate", "is_active"]
    list_editable = ["is_active"]
