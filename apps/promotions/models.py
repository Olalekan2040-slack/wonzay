from django.db import models
from django.contrib.auth import get_user_model
from apps.store.models import Product, Collection

User = get_user_model()


class Coupon(models.Model):
    DISCOUNT_TYPE_CHOICES = [
        ("percentage", "Percentage Off"),
        ("fixed", "Fixed Amount Off"),
        ("free_shipping", "Free Shipping"),
    ]

    code = models.CharField(max_length=50, unique=True)
    description = models.CharField(max_length=200, blank=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPE_CHOICES)
    discount_value = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    minimum_order_value = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    applicable_collections = models.ManyToManyField(Collection, blank=True)
    applicable_products = models.ManyToManyField(Product, blank=True)
    max_uses = models.PositiveIntegerField(null=True, blank=True, help_text="Leave blank for unlimited")
    max_uses_per_customer = models.PositiveIntegerField(default=1)
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code

    @property
    def total_uses(self):
        return self.usages.count()


class CouponUsage(models.Model):
    coupon = models.ForeignKey(Coupon, on_delete=models.CASCADE, related_name="usages")
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True)
    order = models.ForeignKey("orders.Order", on_delete=models.CASCADE)
    used_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.coupon.code} used on order {self.order_id}"
