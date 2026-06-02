from django.utils import timezone
from .models import Coupon, CouponUsage


def apply_coupon(code, cart, user=None):
    try:
        coupon = Coupon.objects.get(code=code, is_active=True)
    except Coupon.DoesNotExist:
        return {"valid": False, "error": "Invalid coupon code."}

    now = timezone.now()
    if now < coupon.valid_from:
        return {"valid": False, "error": "This coupon is not yet active."}
    if coupon.valid_until and now > coupon.valid_until:
        return {"valid": False, "error": "This coupon has expired."}
    if coupon.max_uses and coupon.total_uses >= coupon.max_uses:
        return {"valid": False, "error": "This coupon has reached its usage limit."}
    if cart.subtotal < coupon.minimum_order_value:
        return {
            "valid": False,
            "error": f"Minimum order of ${coupon.minimum_order_value} required.",
        }
    if user and user.is_authenticated:
        uses = CouponUsage.objects.filter(coupon=coupon, user=user).count()
        if uses >= coupon.max_uses_per_customer:
            return {"valid": False, "error": "You have already used this coupon."}

    return {"valid": True, "coupon": coupon}


def calculate_discount(coupon, subtotal, shipping_cost=0):
    if coupon.discount_type == "percentage":
        return min(subtotal * coupon.discount_value / 100, subtotal)
    elif coupon.discount_type == "fixed":
        return min(coupon.discount_value, subtotal)
    elif coupon.discount_type == "free_shipping":
        return shipping_cost
    return 0
