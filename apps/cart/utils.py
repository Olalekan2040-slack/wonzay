from .models import Cart


def get_or_create_cart(request):
    if request.user.is_authenticated:
        cart, _ = Cart.objects.get_or_create(user=request.user)
        return cart
    session_key = request.session.session_key
    if not session_key:
        request.session.create()
        session_key = request.session.session_key
    cart, _ = Cart.objects.get_or_create(session_key=session_key, user=None)
    return cart


def merge_session_cart_into_user_cart(request):
    session_key = request.session.session_key
    if not session_key:
        return
    try:
        session_cart = Cart.objects.get(session_key=session_key, user=None)
    except Cart.DoesNotExist:
        return
    user_cart, _ = Cart.objects.get_or_create(user=request.user)
    for item in session_cart.items.all():
        existing = user_cart.items.filter(product=item.product, variant=item.variant).first()
        if existing:
            existing.quantity += item.quantity
            existing.save()
        else:
            item.cart = user_cart
            item.save()
    session_cart.delete()
