from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.sitemaps.views import sitemap
from apps.store.sitemaps import ProductSitemap, CollectionSitemap
from apps.pages.views import robots_txt

sitemaps = {
    "products": ProductSitemap,
    "collections": CollectionSitemap,
}

urlpatterns = [
    path("admin/", admin.site.urls),
    path("", include("apps.store.urls")),
    path("cart/", include("apps.cart.urls")),
    path("checkout/", include("apps.orders.urls")),
    path("accounts/", include("apps.accounts.urls")),
    path("search/", include("apps.store.search_urls")),
    path("reviews/", include("apps.reviews.urls")),
    path("newsletter/", include("apps.newsletter.urls")),
    path("pages/", include("apps.pages.urls")),
    path("dashboard/", include("apps.dashboard.urls")),
    path("sitemap.xml", sitemap, {"sitemaps": sitemaps}, name="django.contrib.sitemaps.views.sitemap"),
    path("robots.txt", robots_txt, name="robots_txt"),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
