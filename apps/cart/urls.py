from django.urls import path
from . import views

app_name = "cart"

urlpatterns = [
    path("", views.CartView.as_view(), name="detail"),
    path("add/", views.AddToCartView.as_view(), name="add"),
    path("update/", views.UpdateCartView.as_view(), name="update"),
    path("remove/", views.RemoveFromCartView.as_view(), name="remove"),
    path("drawer/", views.CartDrawerView.as_view(), name="drawer"),
    path("apply-coupon/", views.ApplyCouponView.as_view(), name="apply_coupon"),
]
