from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView, DetailView
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.db.models import Sum, Count
from django.utils import timezone
import datetime

from apps.store.models import Product, Collection
from apps.orders.models import Order
from apps.accounts.models import CustomerProfile
from apps.promotions.models import Coupon
from apps.newsletter.models import NewsletterSubscriber
from apps.reviews.models import Review
from apps.content.models import AnnouncementBar, HeroSlide


DASHBOARD_NAV = [
    ("Overview", "dashboard:home", '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 12l2-2m0 0l7-7 7 7M5 10v10a1 1 0 001 1h3m10-11l2 2m-2-2v10a1 1 0 01-1 1h-3m-6 0a1 1 0 001-1v-4a1 1 0 011-1h2a1 1 0 011 1v4a1 1 0 001 1m-6 0h6"/></svg>'),
    ("Products", "dashboard:product_list", '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M20 7l-8-4-8 4m16 0l-8 4m8-4v10l-8 4m0-10L4 7m8 4v10M4 7v10l8 4"/></svg>'),
    ("Collections", "dashboard:collection_list", '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/></svg>'),
    ("Orders", "dashboard:order_list", '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 5H7a2 2 0 00-2 2v12a2 2 0 002 2h10a2 2 0 002-2V7a2 2 0 00-2-2h-2M9 5a2 2 0 002 2h2a2 2 0 002-2M9 5a2 2 0 012-2h2a2 2 0 012 2"/></svg>'),
    ("Customers", "dashboard:customer_list", '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197M13 7a4 4 0 11-8 0 4 4 0 018 0z"/></svg>'),
    ("Coupons", "dashboard:coupon_list", '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 7h.01M7 3h5c.512 0 1.024.195 1.414.586l7 7a2 2 0 010 2.828l-7 7a2 2 0 01-2.828 0l-7-7A1.994 1.994 0 013 12V7a4 4 0 014-4z"/></svg>'),
    ("Reviews", "dashboard:review_moderation", '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11.049 2.927c.3-.921 1.603-.921 1.902 0l1.519 4.674a1 1 0 00.95.69h4.915c.969 0 1.371 1.24.588 1.81l-3.976 2.888a1 1 0 00-.363 1.118l1.518 4.674c.3.922-.755 1.688-1.538 1.118l-3.976-2.888a1 1 0 00-1.176 0l-3.976 2.888c-.783.57-1.838-.197-1.538-1.118l1.518-4.674a1 1 0 00-.363-1.118l-3.976-2.888c-.784-.57-.38-1.81.588-1.81h4.914a1 1 0 00.951-.69l1.519-4.674z"/></svg>'),
    ("Newsletter", "dashboard:newsletter", '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"/></svg>'),
    ("Content", "dashboard:content_blocks", '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 6h16M4 12h16M4 18h7"/></svg>'),
]


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    def test_func(self):
        return self.request.user.is_staff

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["dashboard_nav"] = DASHBOARD_NAV
        return ctx


class DashboardHomeView(StaffRequiredMixin, TemplateView):
    template_name = "dashboard/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        today = timezone.now().date()
        ctx["today_orders"] = Order.objects.filter(created_at__date=today)
        ctx["today_revenue"] = (
            ctx["today_orders"].filter(payment_status="paid").aggregate(Sum("total"))["total__sum"] or 0
        )
        ctx["recent_orders"] = Order.objects.select_related("shipping_address").order_by("-created_at")[:10]
        ctx["low_stock"] = (
            Product.objects.filter(is_active=True, variants__stock_quantity__lte=3)
            .distinct().prefetch_related("images")[:10]
        )
        return ctx


class ProductListView(StaffRequiredMixin, ListView):
    model = Product
    template_name = "dashboard/product_list.html"
    context_object_name = "products"
    paginate_by = 30
    queryset = Product.objects.select_related("collection").prefetch_related("images").order_by("-updated_at")


class ProductCreateView(StaffRequiredMixin, CreateView):
    model = Product
    template_name = "dashboard/product_form.html"
    fields = [
        "name", "description", "price", "compare_at_price", "collection",
        "tags", "is_active", "is_new_arrival", "is_best_seller",
        "meta_title", "meta_description",
    ]
    success_url = reverse_lazy("dashboard:product_list")


class ProductUpdateView(StaffRequiredMixin, UpdateView):
    model = Product
    template_name = "dashboard/product_form.html"
    fields = [
        "name", "description", "price", "compare_at_price", "collection",
        "tags", "is_active", "is_new_arrival", "is_best_seller",
        "meta_title", "meta_description",
    ]
    success_url = reverse_lazy("dashboard:product_list")


class ProductDeleteView(StaffRequiredMixin, DeleteView):
    model = Product
    template_name = "dashboard/product_confirm_delete.html"
    success_url = reverse_lazy("dashboard:product_list")


class CollectionListView(StaffRequiredMixin, ListView):
    model = Collection
    template_name = "dashboard/collection_list.html"
    context_object_name = "collections"


class CollectionCreateView(StaffRequiredMixin, CreateView):
    model = Collection
    template_name = "dashboard/collection_form.html"
    fields = ["name", "description", "cover_image", "is_active", "order"]
    success_url = reverse_lazy("dashboard:collection_list")


class CollectionUpdateView(StaffRequiredMixin, UpdateView):
    model = Collection
    template_name = "dashboard/collection_form.html"
    fields = ["name", "description", "cover_image", "is_active", "order"]
    success_url = reverse_lazy("dashboard:collection_list")


class OrderListView(StaffRequiredMixin, ListView):
    model = Order
    template_name = "dashboard/order_list.html"
    context_object_name = "orders"
    paginate_by = 30
    queryset = Order.objects.select_related("shipping_address").order_by("-created_at")


class OrderDetailView(StaffRequiredMixin, DetailView):
    model = Order
    template_name = "dashboard/order_detail.html"
    context_object_name = "order"


class CustomerListView(StaffRequiredMixin, ListView):
    template_name = "dashboard/customer_list.html"
    context_object_name = "customers"

    def get_queryset(self):
        from django.contrib.auth import get_user_model
        return get_user_model().objects.filter(is_staff=False).annotate(order_count=Count("orders"))


class CouponListView(StaffRequiredMixin, ListView):
    model = Coupon
    template_name = "dashboard/coupon_list.html"
    context_object_name = "coupons"


class CouponCreateView(StaffRequiredMixin, CreateView):
    model = Coupon
    template_name = "dashboard/coupon_form.html"
    fields = [
        "code", "description", "discount_type", "discount_value",
        "minimum_order_value", "max_uses", "max_uses_per_customer",
        "is_active", "valid_from", "valid_until",
    ]
    success_url = reverse_lazy("dashboard:coupon_list")


class ContentBlocksView(StaffRequiredMixin, TemplateView):
    template_name = "dashboard/content_blocks.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["announcement_bars"] = AnnouncementBar.objects.all()
        ctx["hero_slides"] = HeroSlide.objects.all()
        return ctx


class ReviewModerationView(StaffRequiredMixin, ListView):
    model = Review
    template_name = "dashboard/review_moderation.html"
    context_object_name = "reviews"
    queryset = Review.objects.select_related("author", "product").order_by("is_approved", "-created_at")


class NewsletterView(StaffRequiredMixin, ListView):
    model = NewsletterSubscriber
    template_name = "dashboard/newsletter.html"
    context_object_name = "subscribers"
    queryset = NewsletterSubscriber.objects.order_by("-subscribed_at")
