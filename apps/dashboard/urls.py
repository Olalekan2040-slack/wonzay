from django.urls import path
from . import views

app_name = "dashboard"

urlpatterns = [
    path("", views.DashboardHomeView.as_view(), name="home"),
    path("products/", views.ProductListView.as_view(), name="product_list"),
    path("products/add/", views.ProductCreateView.as_view(), name="product_add"),
    path("products/<int:pk>/edit/", views.ProductUpdateView.as_view(), name="product_edit"),
    path("products/<int:pk>/delete/", views.ProductDeleteView.as_view(), name="product_delete"),
    path("collections/", views.CollectionListView.as_view(), name="collection_list"),
    path("collections/add/", views.CollectionCreateView.as_view(), name="collection_add"),
    path("collections/<int:pk>/edit/", views.CollectionUpdateView.as_view(), name="collection_edit"),
    path("orders/", views.OrderListView.as_view(), name="order_list"),
    path("orders/<int:pk>/", views.OrderDetailView.as_view(), name="order_detail"),
    path("orders/<int:pk>/update-status/", views.OrderUpdateStatusView.as_view(), name="order_update_status"),
    path("customers/", views.CustomerListView.as_view(), name="customer_list"),
    path("coupons/", views.CouponListView.as_view(), name="coupon_list"),
    path("coupons/add/", views.CouponCreateView.as_view(), name="coupon_add"),
    path("content/", views.ContentBlocksView.as_view(), name="content_blocks"),
    path("reviews/", views.ReviewModerationView.as_view(), name="review_moderation"),
    path("reviews/<int:pk>/approve/", views.ReviewApproveView.as_view(), name="review_approve"),
    path("reviews/<int:pk>/delete/", views.ReviewDeleteView.as_view(), name="review_delete"),
    path("newsletter/", views.NewsletterView.as_view(), name="newsletter"),
    path("newsletter/send/", views.NewsletterSendView.as_view(), name="newsletter_send"),
    path("staff/", views.StaffListView.as_view(), name="staff_list"),
    path("staff/create/", views.StaffCreateView.as_view(), name="staff_create"),
    path("staff/<int:pk>/revoke/", views.StaffRevokeView.as_view(), name="staff_revoke"),
]