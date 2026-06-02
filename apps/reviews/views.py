from django.views import View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect, get_object_or_404
from django.contrib import messages
from apps.store.models import Product
from .models import Review


class SubmitReviewView(LoginRequiredMixin, View):
    def post(self, request, product_slug):
        product = get_object_or_404(Product, slug=product_slug, is_active=True)
        if Review.objects.filter(product=product, author=request.user).exists():
            messages.error(request, "You have already reviewed this product.")
            return redirect(product.get_absolute_url())
        Review.objects.create(
            product=product,
            author=request.user,
            rating=int(request.POST.get("rating", 5)),
            title=request.POST.get("title", ""),
            body=request.POST.get("body", ""),
        )
        messages.success(request, "Review submitted — it will appear once approved.")
        return redirect(product.get_absolute_url())
