from django.views.generic import TemplateView, DetailView, View
from django.shortcuts import redirect, get_object_or_404
from django.http import HttpResponse, JsonResponse, HttpResponseBadRequest
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib import messages
from django.conf import settings
from .models import Order, ShippingAddress, OrderItem, ShippingRate
from apps.cart.utils import get_or_create_cart
import stripe
import json


class CheckoutView(LoginRequiredMixin, TemplateView):
    template_name = "orders/checkout.html"
    login_url = "/accounts/login/"
    redirect_field_name = "next"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["cart"] = get_or_create_cart(self.request)
        ctx["shipping_rates"] = ShippingRate.objects.filter(is_active=True, country_code="AU")
        return ctx

    def post(self, request):
        cart = get_or_create_cart(request)
        if not cart or not cart.items.exists():
            return redirect("cart:detail")

        rate_id = request.POST.get("shipping_rate_id")
        rate = ShippingRate.objects.filter(pk=rate_id).first() if rate_id else None

        shipping_rates = ShippingRate.objects.filter(is_active=True, country_code="AU")
        if shipping_rates.exists() and not rate:
            return self.render_to_response({
                **self.get_context_data(),
                "error": "Please select a shipping method.",
            })
        if not request.POST.get("full_name", "").strip():
            return self.render_to_response({
                **self.get_context_data(),
                "error": "Please enter your full name.",
            })

        address = ShippingAddress.objects.create(
            full_name=request.POST.get("full_name", ""),
            address_line1=request.POST.get("address_line1", ""),
            address_line2=request.POST.get("address_line2", ""),
            city=request.POST.get("city", ""),
            state=request.POST.get("state", ""),
            postcode=request.POST.get("postcode", ""),
            country=request.POST.get("country", "Australia"),
            phone=request.POST.get("phone", ""),
        )

        shipping_cost = rate.rate if rate else 0
        subtotal = cart.subtotal
        total = subtotal + shipping_cost

        order = Order.objects.create(
            customer=request.user if request.user.is_authenticated else None,
            guest_email=request.POST.get("email", ""),
            guest_phone=request.POST.get("phone", ""),
            shipping_address=address,
            shipping_rate=rate,
            subtotal=subtotal,
            shipping_cost=shipping_cost,
            total=total,
        )
        for item in cart.items.select_related("product", "variant"):
            OrderItem.objects.create(
                order=order,
                product=item.product,
                variant=item.variant,
                product_name=item.product.name,
                variant_label=str(item.variant) if item.variant else "",
                unit_price=item.unit_price,
                quantity=item.quantity,
                line_total=item.line_total,
            )

        # Send order confirmation email
        from apps.utils.emails import send_order_confirmation
        send_order_confirmation(order)

        request.session["pending_order_id"] = order.id
        return redirect("orders:payment")


class PaymentView(TemplateView):
    template_name = "orders/payment.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        order_id = self.request.session.get("pending_order_id")
        if order_id:
            ctx["order"] = Order.objects.filter(pk=order_id).first()
        ctx["stripe_public_key"] = settings.STRIPE_PUBLIC_KEY
        return ctx


class CreatePaymentIntentView(View):
    def post(self, request):
        try:
            data = json.loads(request.body)
        except json.JSONDecodeError:
            return HttpResponseBadRequest("Invalid JSON")

        order_id = data.get("order_id")
        pending_order_id = request.session.get("pending_order_id")
        if not order_id or str(order_id) != str(pending_order_id):
            return HttpResponseBadRequest("Invalid order")

        order = get_object_or_404(Order, pk=order_id)
        if order.payment_status == "paid":
            return HttpResponseBadRequest("Order already paid")

        stripe.api_key = settings.STRIPE_SECRET_KEY
        try:
            intent = stripe.PaymentIntent.create(
                amount=int(order.total * 100),
                currency="aud",
                metadata={"order_id": str(order.id), "order_number": order.order_number},
            )
        except stripe.error.StripeError as exc:
            return JsonResponse({"error": str(exc)}, status=400)

        order.stripe_payment_intent = intent.id
        order.save(update_fields=["stripe_payment_intent"])

        return JsonResponse({"client_secret": intent.client_secret})


class OrderSuccessView(DetailView):
    model = Order
    template_name = "orders/success.html"
    context_object_name = "order"
    pk_url_kwarg = "order_id"


@method_decorator(csrf_exempt, name="dispatch")
class StripeWebhookView(View):
    def post(self, request):
        payload = request.body
        sig_header = request.META.get("HTTP_STRIPE_SIGNATURE", "")
        try:
            event = stripe.Webhook.construct_event(
                payload, sig_header, settings.STRIPE_WEBHOOK_SECRET
            )
        except (ValueError, stripe.error.SignatureVerificationError):
            return HttpResponse(status=400)

        if event["type"] == "payment_intent.succeeded":
            pi = event["data"]["object"]
            Order.objects.filter(stripe_payment_intent=pi["id"]).update(
                payment_status="paid", status="processing"
            )
        return HttpResponse(status=200)
