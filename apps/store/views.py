from django.views.generic import TemplateView, ListView, DetailView, View
from django.http import JsonResponse
from django.db.models import Q, Avg
from .models import Product, Collection


class HomeView(TemplateView):
    template_name = "store/home.html"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["new_arrivals"] = (
            Product.objects.filter(is_active=True, is_new_arrival=True)
            .select_related("collection")
            .prefetch_related("images")[:12]
        )
        ctx["best_sellers"] = (
            Product.objects.filter(is_active=True, is_best_seller=True)
            .select_related("collection")
            .prefetch_related("images")[:12]
        )
        ctx["collections"] = Collection.objects.filter(is_active=True)
        from apps.content.models import HeroSlide, TrustBadge, BrandStory
        from apps.reviews.models import Review
        ctx["hero_slides"] = HeroSlide.objects.filter(is_active=True)
        ctx["trust_badges"] = TrustBadge.objects.filter(is_active=True)
        ctx["brand_story"] = BrandStory.objects.first()
        ctx["featured_reviews"] = (
            Review.objects.filter(is_approved=True, is_featured=True)
            .select_related("author", "product")
            .prefetch_related("product__images")[:8]
        )
        return ctx


class CollectionListView(ListView):
    model = Collection
    template_name = "store/collection_list.html"
    context_object_name = "collections"
    queryset = Collection.objects.filter(is_active=True)


class CollectionDetailView(DetailView):
    model = Collection
    template_name = "store/collection_detail.html"
    context_object_name = "collection"

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        products = self.object.products.filter(is_active=True).prefetch_related("images", "variants")
        sort = self.request.GET.get("sort", "featured")
        if sort == "price_asc":
            products = products.order_by("price")
        elif sort == "price_desc":
            products = products.order_by("-price")
        elif sort == "newest":
            products = products.order_by("-created_at")
        ctx["products"] = products
        ctx["sort"] = sort
        return ctx


class ProductDetailView(DetailView):
    model = Product
    template_name = "store/product_detail.html"
    context_object_name = "product"
    queryset = Product.objects.filter(is_active=True).prefetch_related(
        "images", "variants", "reviews__author"
    ).select_related("collection")

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        product = self.object
        ctx["related_products"] = (
            Product.objects.filter(collection=product.collection, is_active=True)
            .exclude(pk=product.pk)
            .prefetch_related("images")[:8]
        )
        # Clear model ordering before DISTINCT so SQLite only deduplicates
        # on the selected column, not on (size, colour) pairs.
        ctx["sizes"] = (
            product.variants.order_by("size")
            .values_list("size", flat=True)
            .distinct()
        )
        ctx["colours"] = (
            product.variants.order_by("colour")
            .values_list("colour", flat=True)
            .distinct()
        )
        import json
        ctx["variants_json"] = json.dumps([
            {
                "id": v.pk,
                "size": v.size,
                "colour": v.colour,
                "stock_status": v.stock_status,
                "is_available": v.is_available and v.stock_quantity > 0,
            }
            for v in product.variants.all()
        ])
        from apps.reviews.models import Review
        ctx["reviews"] = Review.objects.filter(product=product, is_approved=True).select_related("author")
        return ctx


class SearchView(ListView):
    template_name = "store/search_results.html"
    context_object_name = "products"
    paginate_by = 24

    def get_queryset(self):
        q = self.request.GET.get("q", "").strip()
        if not q:
            return Product.objects.none()
        return (
            Product.objects.filter(is_active=True)
            .filter(
                Q(name__icontains=q)
                | Q(description__icontains=q)
                | Q(tags__name__icontains=q)
                | Q(collection__name__icontains=q)
            )
            .distinct()
            .prefetch_related("images")
        )

    def get_context_data(self, **kwargs):
        ctx = super().get_context_data(**kwargs)
        ctx["query"] = self.request.GET.get("q", "")
        return ctx


class AjaxSearchView(View):
    def get(self, request):
        q = request.GET.get("q", "").strip()
        results = []
        if len(q) >= 2:
            products = (
                Product.objects.filter(is_active=True)
                .filter(Q(name__icontains=q) | Q(tags__name__icontains=q))
                .distinct()
                .prefetch_related("images")[:5]
            )
            for p in products:
                img = p.primary_image
                results.append({
                    "name": p.name,
                    "url": p.get_absolute_url(),
                    "price": str(p.price),
                    "image": img.image.url if img else "",
                })
        return JsonResponse({"results": results})
