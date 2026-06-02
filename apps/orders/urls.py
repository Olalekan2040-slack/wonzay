from django.urls import path
from . import views

app_name = "orders"

urlpatterns = [
    path("", views.CheckoutView.as_view(), name="checkout"),
    path("payment/", views.PaymentView.as_view(), name="payment"),
    path("stripe/webhook/", views.StripeWebhookView.as_view(), name="stripe_webhook"),
    path("<int:order_id>/success/", views.OrderSuccessView.as_view(), name="success"),
]
