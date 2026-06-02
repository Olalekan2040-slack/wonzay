from django.db import models
from django.contrib.auth import get_user_model
from apps.store.models import Product, ProductVariant

User = get_user_model()


class Cart(models.Model):
    session_key = models.CharField(max_length=40, blank=True, db_index=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE, null=True, blank=True, related_name="cart")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart ({self.user or self.session_key[:8]})"

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def subtotal(self):
        return sum(item.line_total for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("cart", "product", "variant")

    def __str__(self):
        return f"{self.quantity}× {self.product.name}"

    @property
    def unit_price(self):
        return self.product.price

    @property
    def line_total(self):
        return self.unit_price * self.quantity
