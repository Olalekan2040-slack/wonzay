from django.views import View
from django.views.generic import TemplateView
from django.http import JsonResponse
from django.shortcuts import redirect, render
from django.contrib import messages
from .models import CartItem
from .utils import get_or_create_cart
from apps.store.models import ProductVariant, Product
from apps.promotions.utils import apply_coupon


class CartView(TemplateView):
    template_name = "cart/cart.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["cart"] = get_or_create_cart(self.request)
        return ctx


class AddToCartView(View):
    def post(self, request):
        is_ajax = request.headers.get("X-Requested-With") == "XMLHttpRequest"
        cart = get_or_create_cart(request)
        product_id = request.POST.get("product_id", "").strip()
        variant_id = request.POST.get("variant_id", "").strip()

        try:
            quantity = max(1, int(request.POST.get("quantity", 1)))
        except (ValueError, TypeError):
            quantity = 1

        if not product_id:
            if is_ajax:
                return JsonResponse({"success": False, "error": "No product specified."}, status=400)
            messages.error(request, "No product specified.")
            return redirect("cart:detail")

        try:
            product = Product.objects.get(pk=product_id, is_active=True)
        except Product.DoesNotExist:
            if is_ajax:
                return JsonResponse({"success": False, "error": "Product not found."}, status=404)
            messages.error(request, "Product not found.")
            return redirect("store:home")

        # Resolve variant — if an ID was supplied, it must exist
        variant = None
        if variant_id:
            try:
                variant = ProductVariant.objects.get(pk=variant_id, product=product)
            except ProductVariant.DoesNotExist:
                if is_ajax:
                    return JsonResponse({"success": False, "error": "Selected variant not found."}, status=404)
                messages.error(request, "Selected size/colour is no longer available.")
                return redirect(product.get_absolute_url())

        # Add or update cart line
        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            variant=variant,
            defaults={"quantity": quantity},
        )
        if not created:
            item.quantity += quantity
            item.save()

        # Persist session so the cookie is set on the response
        request.session.modified = True

        if is_ajax:
            return JsonResponse({
                "success": True,
                "cart_count": cart.total_items,
                "product_name": product.name,
            })

        messages.success(request, f'"{product.name}" added to your cart.')
        return redirect("cart:detail")


class UpdateCartView(View):
    def post(self, request):
        cart = get_or_create_cart(request)
        item_id = request.POST.get("item_id")
        quantity = int(request.POST.get("quantity", 1))
        try:
            item = CartItem.objects.get(pk=item_id, cart=cart)
            item.quantity = max(1, quantity)
            item.save()
        except CartItem.DoesNotExist:
            pass
        return redirect("cart:detail")


class RemoveFromCartView(View):
    def post(self, request):
        cart = get_or_create_cart(request)
        item_id = request.POST.get("item_id")
        CartItem.objects.filter(pk=item_id, cart=cart).delete()
        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return JsonResponse({"success": True, "cart_count": cart.total_items})
        return redirect("cart:detail")


class CartDrawerView(TemplateView):
    template_name = "cart/drawer.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        cart = get_or_create_cart(self.request)
        ctx["cart"] = cart
        ctx["cart_items"] = cart.items.select_related("product", "variant").all()
        ctx["cart_total"] = cart.subtotal
        ctx["cart"] = cart
        return ctx


class ApplyCouponView(View):
    def post(self, request):
        code = request.POST.get("coupon_code", "").strip().upper()
        cart = get_or_create_cart(request)
        result = apply_coupon(code, cart, request.user)
        if result["valid"]:
            request.session["coupon_code"] = code
            messages.success(request, f"Coupon '{code}' applied!")
        else:
            messages.error(request, result["error"])
        return redirect("cart:detail")
