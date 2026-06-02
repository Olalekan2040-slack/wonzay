from django.contrib.sitemaps import Sitemap
from .models import Product, Collection


class ProductSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Product.objects.filter(is_active=True)

    def lastmod(self, obj):
        return obj.updated_at


class CollectionSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.6

    def items(self):
        return Collection.objects.filter(is_active=True)
