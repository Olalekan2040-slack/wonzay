import uuid
from django.db import models
from django.contrib.auth import get_user_model
from apps.store.models import Product, ProductVariant

User = get_user_model()


class ShippingRate(models.Model):
    name = models.CharField(max_length=100)
    country_code = models.CharField(max_length=2, default="AU")
    rate = models.DecimalField(max_digits=8, decimal_places=2)
    estimated_days_min = models.PositiveIntegerField(default=3)
    estimated_days_max = models.PositiveIntegerField(default=7)
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.country_code}) – ${self.rate}"


class ShippingAddress(models.Model):
    full_name = models.CharField(max_length=200)
    address_line1 = models.CharField(max_length=255)
    address_line2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100)
    state = models.CharField(max_length=100)
    postcode = models.CharField(max_length=20)
    country = models.CharField(max_length=100, default="Australia")
    country_code = models.CharField(max_length=2, default="AU")
    phone = models.CharField(max_length=30, blank=True)

    def __str__(self):
        return f"{self.full_name}, {self.city} {self.postcode}"


class Order(models.Model):
    STATUS_CHOICES = [
        ("pending", "Pending"),
        ("processing", "Processing"),
        ("shipped", "Shipped"),
        ("delivered", "Delivered"),
        ("cancelled", "Cancelled"),
        ("refunded", "Refunded"),
    ]
    PAYMENT_STATUS_CHOICES = [
        ("unpaid", "Unpaid"),
        ("paid", "Paid"),
        ("refunded", "Refunded"),
        ("failed", "Failed"),
    ]
    PAYMENT_METHOD_CHOICES = [
        ("stripe", "Credit / Debit Card"),
        ("paypal", "PayPal"),
        ("afterpay", "AfterPay"),
    ]

    order_number = models.CharField(max_length=36, unique=True, default=uuid.uuid4, db_index=True)
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True,
                                 related_name="orders", db_index=True)
    guest_email = models.EmailField(blank=True)
    guest_phone = models.CharField(max_length=30, blank=True)
    shipping_address = models.ForeignKey(ShippingAddress, on_delete=models.PROTECT, null=True)
    shipping_rate = models.ForeignKey(ShippingRate, on_delete=models.SET_NULL, null=True, blank=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default="pending")
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    shipping_cost = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    discount_amount = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2)
    coupon = models.ForeignKey("promotions.Coupon", on_delete=models.SET_NULL, null=True, blank=True)
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, blank=True)
    payment_status = models.CharField(max_length=20, choices=PAYMENT_STATUS_CHOICES, default="unpaid")
    stripe_payment_intent = models.CharField(max_length=200, blank=True)
    paypal_order_id = models.CharField(max_length=200, blank=True)
    tracking_number = models.CharField(max_length=200, blank=True)
    tracking_carrier = models.CharField(max_length=100, blank=True)
    notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["order_number", "customer"])]

    def __str__(self):
        return f"Order #{str(self.order_number)[:8].upper()}"

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse("orders:success", kwargs={"order_id": self.id})


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    variant = models.ForeignKey(ProductVariant, on_delete=models.SET_NULL, null=True, blank=True)
    product_name = models.CharField(max_length=200)
    variant_label = models.CharField(max_length=100, blank=True)
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()
    line_total = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f"{self.quantity}× {self.product_name}"
