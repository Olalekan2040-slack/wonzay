from django.views.generic import TemplateView, ListView, CreateView, UpdateView, DeleteView, DetailView, View
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.db.models import Sum, Count
from django.utils import timezone
from django.shortcuts import redirect, get_object_or_404, render
from django.contrib import messages
from django.http import JsonResponse
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
    ("Staff", "dashboard:staff_list", '<svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 4.354a4 4 0 110 5.292M15 21H3v-1a6 6 0 0112 0v1zm0 0h6v-1a6 6 0 00-9-5.197"/></svg>'),
]


class StaffRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Accessible to any staff user (is_staff=True) or superuser."""
    login_url = "/accounts/login/"

    def test_func(self):
        return self.request.user.is_staff or self.request.user.is_superuser

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["dashboard_nav"] = DASHBOARD_NAV
        ctx["is_superuser"] = self.request.user.is_superuser
        return ctx


class SuperuserRequiredMixin(LoginRequiredMixin, UserPassesTestMixin):
    """Accessible only to superusers — blocks regular staff."""
    login_url = "/accounts/login/"

    def test_func(self):
        return self.request.user.is_superuser

    def handle_no_permission(self):
        messages.error(self.request, "This action requires superuser access.")
        return redirect("dashboard:home")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["dashboard_nav"] = DASHBOARD_NAV
        ctx["is_superuser"] = True
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


# ── Order status + tracking ───────────────────────────────────────────────────

class OrderUpdateStatusView(StaffRequiredMixin, View):
    """Update order status and optionally email the customer."""

    def post(self, request, pk):
        order = get_object_or_404(Order, pk=pk)
        new_status = request.POST.get("status")
        tracking_number = request.POST.get("tracking_number", "").strip()
        tracking_carrier = request.POST.get("tracking_carrier", "").strip()
        send_email = request.POST.get("send_email") == "1"

        valid = [s for s, _ in Order.STATUS_CHOICES]
        if new_status not in valid:
            messages.error(request, "Invalid status.")
            return redirect("dashboard:order_detail", pk=pk)

        order.status = new_status
        if tracking_number:
            order.tracking_number = tracking_number
        if tracking_carrier:
            order.tracking_carrier = tracking_carrier
        order.save()

        if send_email:
            recipient = order.customer.email if order.customer else order.guest_email
            if recipient:
                _send_order_status_email(order, recipient, tracking_number, tracking_carrier)
                messages.success(request, f"Status updated to '{new_status}' and email sent to {recipient}.")
            else:
                messages.warning(request, f"Status updated but no email address on file.")
        else:
            messages.success(request, f"Order #{order.pk} status updated to '{new_status}'.")

        return redirect("dashboard:order_detail", pk=pk)


def _send_order_status_email(order, recipient, tracking_number="", tracking_carrier=""):
    from apps.utils.emails import _wrap, _send

    name = (
        order.customer.first_name if order.customer and order.customer.first_name
        else order.shipping_address.full_name.split()[0] if order.shipping_address
        else "Customer"
    )

    status_messages = {
        "processing": ("Your order is being processed", "We're preparing your order and it will be dispatched soon."),
        "shipped":    ("Your order has been shipped! 📦", "Great news — your order is on its way!"),
        "delivered":  ("Your order has been delivered ✅", "Your order has been delivered. We hope you love it!"),
        "cancelled":  ("Your order has been cancelled", "Your order has been cancelled. If you have questions, please contact us."),
        "refunded":   ("Your refund has been processed", "Your refund has been processed and should appear within 3–5 business days."),
    }
    subject_prefix, status_text = status_messages.get(
        order.status, ("Your order has been updated", "Your order status has been updated.")
    )

    tracking_html = ""
    if tracking_number:
        carrier_text = f" via {tracking_carrier}" if tracking_carrier else ""
        tracking_html = f"""
        <div style="background:#F7F5FF;border-radius:10px;padding:16px 20px;margin:16px 0;border-left:4px solid #5B4B8A;">
          <p style="margin:0 0 4px;font-size:12px;font-weight:700;text-transform:uppercase;letter-spacing:0.08em;color:#A7A3C0;">Tracking Information</p>
          <p style="margin:0;font-size:15px;font-weight:700;color:#2D1563;">{tracking_number}{carrier_text}</p>
        </div>"""

    html = _wrap(f"Order #{order.pk} — {subject_prefix}", f"""
      <h1 style="font-family:Georgia,serif;font-size:24px;font-weight:700;color:#1A0A38;margin:0 0 10px;">
        Hi {name}, {subject_prefix.lower()}
      </h1>
      <p style="font-size:15px;color:#3D2F5C;line-height:1.7;margin:0 0 16px;">{status_text}</p>
      <div style="background:#F7F5FF;border-radius:10px;padding:14px 20px;margin:0 0 16px;display:inline-block;">
        <p style="margin:0;font-size:12px;color:#A7A3C0;text-transform:uppercase;letter-spacing:0.08em;">Order Number</p>
        <p style="margin:4px 0 0;font-size:18px;font-weight:700;color:#2D1563;">#{order.pk}</p>
      </div>
      {tracking_html}
      <p style="font-size:13px;color:#6B6B7C;line-height:1.6;margin:16px 0 0;">
        Questions? Reply to this email or contact us at
        <a href="mailto:wonzayskollections@gmail.com" style="color:#5B4B8A;">wonzayskollections@gmail.com</a>
      </p>
    """)
    text = f"Hi {name}, your order #{order.pk} status is now: {order.status}.\n"
    if tracking_number:
        text += f"Tracking: {tracking_number}\n"
    text += "\nWonzays Kollections"

    _send(f"Order #{order.pk} — {subject_prefix}", recipient, html, text)


# ── Newsletter bulk email ─────────────────────────────────────────────────────

class NewsletterSendView(StaffRequiredMixin, View):
    """Send a one-off email blast to all active subscribers."""

    def get(self, request):
        subscriber_count = NewsletterSubscriber.objects.filter(is_active=True).count()
        return render(request, "dashboard/newsletter_send.html", {
            "dashboard_nav": DASHBOARD_NAV,
            "is_superuser": request.user.is_superuser,
            "subscriber_count": subscriber_count,
        })

    def post(self, request):
        subject = request.POST.get("subject", "").strip()
        body_text = request.POST.get("body", "").strip()

        if not subject or not body_text:
            messages.error(request, "Subject and body are required.")
            return redirect("dashboard:newsletter_send")

        from apps.utils.emails import _wrap, _send
        import re
        # Convert line breaks to <p> tags for HTML
        paragraphs = [p.strip() for p in re.split(r'\n\s*\n', body_text) if p.strip()]
        body_html_inner = "".join(
            f'<p style="font-size:15px;color:#3D2F5C;line-height:1.75;margin:0 0 14px;">{p}</p>'
            for p in paragraphs
        )
        html_template = _wrap(subject, f"""
          <h1 style="font-family:Georgia,serif;font-size:24px;font-weight:700;color:#1A0A38;margin:0 0 20px;">{subject}</h1>
          {body_html_inner}
          <hr style="border:none;border-top:1px solid #E8E4F5;margin:24px 0;" />
          <p style="font-size:12px;color:#C4B8E8;line-height:1.6;">
            You're receiving this because you subscribed at wonzayskollections.com.au.
            <a href="https://wonzayskollections.com.au/newsletter/unsubscribe/" style="color:#A7A3C0;">Unsubscribe</a>.
          </p>
        """)

        subscribers = NewsletterSubscriber.objects.filter(is_active=True)
        sent = 0
        failed = 0
        for sub in subscribers:
            ok = _send(subject, sub.email, html_template, body_text)
            if ok:
                sent += 1
            else:
                failed += 1

        messages.success(request, f"Email sent to {sent} subscriber(s).{' ' + str(failed) + ' failed.' if failed else ''}")
        return redirect("dashboard:newsletter")


# ── Review approve/reject ────────────────────────────────────────────────────

class ReviewApproveView(StaffRequiredMixin, View):
    def post(self, request, pk):
        review = get_object_or_404(Review, pk=pk)
        review.is_approved = not review.is_approved
        review.save()
        status = "approved" if review.is_approved else "hidden"
        messages.success(request, f"Review by {review.author} {status}.")
        return redirect("dashboard:review_moderation")


class ReviewDeleteView(StaffRequiredMixin, View):
    def post(self, request, pk):
        review = get_object_or_404(Review, pk=pk)
        review.delete()
        messages.success(request, "Review deleted.")
        return redirect("dashboard:review_moderation")


# ── Staff user management (superuser only) ───────────────────────────────────

class StaffListView(SuperuserRequiredMixin, TemplateView):
    template_name = "dashboard/staff_list.html"

    def get_context_data(self, **kwargs):
        from django.contrib.auth import get_user_model
        ctx = super().get_context_data(**kwargs)
        ctx["staff_users"] = get_user_model().objects.filter(is_staff=True).order_by("email")
        return ctx


class StaffCreateView(SuperuserRequiredMixin, View):
    """Create a staff user (is_staff=True, is_superuser=False)."""

    def post(self, request):
        from django.contrib.auth import get_user_model
        User = get_user_model()
        email = request.POST.get("email", "").strip().lower()
        first_name = request.POST.get("first_name", "").strip()
        last_name = request.POST.get("last_name", "").strip()
        password = request.POST.get("password", "")

        if not email or not password:
            messages.error(request, "Email and password are required.")
            return redirect("dashboard:staff_list")

        if User.objects.filter(username=email).exists():
            messages.error(request, f"{email} is already registered.")
            return redirect("dashboard:staff_list")

        user = User.objects.create_user(
            username=email, email=email, password=password,
            first_name=first_name, last_name=last_name,
            is_staff=True, is_superuser=False,
        )
        messages.success(request, f"Staff account created for {email}.")
        return redirect("dashboard:staff_list")


class StaffRevokeView(SuperuserRequiredMixin, View):
    """Remove staff access from a user."""

    def post(self, request, pk):
        from django.contrib.auth import get_user_model
        user = get_object_or_404(get_user_model(), pk=pk)
        if user == request.user:
            messages.error(request, "You cannot revoke your own staff access.")
            return redirect("dashboard:staff_list")
        user.is_staff = False
        user.save()
        messages.success(request, f"Staff access removed from {user.email}.")
        return redirect("dashboard:staff_list")
