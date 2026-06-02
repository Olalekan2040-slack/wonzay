from .utils import get_or_create_cart


def cart(request):
    cart_obj = get_or_create_cart(request)
    return {
        "cart": cart_obj,
        "cart_item_count": cart_obj.total_items if cart_obj else 0,
    }
