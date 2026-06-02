from django.views.generic import TemplateView, CreateView, View
from django.contrib.auth import login, logout, authenticate, get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, render
from django.urls import reverse_lazy
from django.http import JsonResponse
from .models import CustomerProfile, Wishlist, WishlistItem
from apps.orders.models import Order
from apps.store.models import Product

User = get_user_model()


class RegisterView(View):
    template_name = "accounts/register.html"

    def get(self, request):
        return render(request, self.template_name)

    def post(self, request):
        email = request.POST.get("email", "").lower()
        password = request.POST.get("password", "")
        first_name = request.POST.get("first_name", "")
        last_name = request.POST.get("last_name", "")
        if User.objects.filter(username=email).exists():
            return render(request, self.template_name, {"error": "Email already registered."})
        user = User.objects.create_user(
            username=email, email=email, password=password,
            first_name=first_name, last_name=last_name,
        )
        CustomerProfile.objects.create(user=user)
        Wishlist.objects.create(user=user)
        login(request, user)
        from apps.cart.utils import merge_session_cart_into_user_cart
        merge_session_cart_into_user_cart(request)
        return redirect("accounts:profile")


class LoginView(View):
    template_name = "accounts/login.html"

    def get(self, request):
        return render(request, self.template_name, {"next": request.GET.get("next", "")})

    def post(self, request):
        email = request.POST.get("email", "").lower()
        password = request.POST.get("password", "")
        user = authenticate(request, username=email, password=password)
        if user:
            login(request, user)
            from apps.cart.utils import merge_session_cart_into_user_cart
            merge_session_cart_into_user_cart(request)
            next_url = request.POST.get("next") or "accounts:profile"
            return redirect(next_url)
        return render(request, self.template_name, {"error": "Invalid email or password."})


class LogoutView(View):
    def get(self, request):
        logout(request)
        return redirect("store:home")

    def post(self, request):
        logout(request)
        return redirect("store:home")


PROFILE_NAV = [
    ("Profile", "accounts:profile"),
    ("Order History", "accounts:order_history"),
    ("Wishlist", "accounts:wishlist"),
]


class ProfileView(LoginRequiredMixin, View):
    template_name = "accounts/profile.html"

    def get(self, request):
        return render(request, self.template_name, {"profile_nav": PROFILE_NAV})

    def post(self, request):
        action = request.POST.get("action")
        if action == "update_profile":
            user = request.user
            user.first_name = request.POST.get("first_name", "")
            user.last_name = request.POST.get("last_name", "")
            user.email = request.POST.get("email", user.email)
            user.save()
            if hasattr(user, "profile"):
                user.profile.phone = request.POST.get("phone", "")
                dob = request.POST.get("date_of_birth", "")
                if dob:
                    from datetime import date
                    try:
                        user.profile.date_of_birth = date.fromisoformat(dob)
                    except ValueError:
                        pass
                user.profile.save()
            from django.contrib import messages as msg
            msg.success(request, "Profile updated successfully.")
        elif action == "change_password":
            old_pw = request.POST.get("old_password", "")
            new_pw = request.POST.get("new_password", "")
            if request.user.check_password(old_pw) and len(new_pw) >= 8:
                request.user.set_password(new_pw)
                request.user.save()
                # update_session_auth_hash keeps the user logged in after
                # password change without needing to call login() (which
                # requires a specific backend when multiple are configured).
                from django.contrib.auth import update_session_auth_hash
                update_session_auth_hash(request, request.user)
                from django.contrib import messages as msg
                msg.success(request, "Password changed successfully.")
            elif not request.user.check_password(old_pw):
                from django.contrib import messages as msg
                msg.error(request, "Current password is incorrect.")
            else:
                from django.contrib import messages as msg
                msg.error(request, "New password must be at least 8 characters.")
        return redirect("accounts:profile")


class OrderHistoryView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/order_history.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["orders"] = Order.objects.filter(customer=self.request.user).prefetch_related("items")
        ctx["profile_nav"] = PROFILE_NAV
        return ctx


class WishlistView(LoginRequiredMixin, TemplateView):
    template_name = "accounts/wishlist.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        wishlist, _ = Wishlist.objects.get_or_create(user=self.request.user)
        ctx["wishlist_items"] = wishlist.items.select_related("product").prefetch_related("product__images")
        ctx["profile_nav"] = PROFILE_NAV
        return ctx


class ToggleWishlistView(LoginRequiredMixin, View):
    def post(self, request):
        product_id = request.POST.get("product_id")
        product = Product.objects.get(pk=product_id)
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        item = WishlistItem.objects.filter(wishlist=wishlist, product=product).first()
        if item:
            item.delete()
            added = False
        else:
            WishlistItem.objects.create(wishlist=wishlist, product=product)
            added = True
        return JsonResponse({"added": added})
