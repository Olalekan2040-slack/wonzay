from django.contrib import admin
from .models import Collection, Product, ProductImage, ProductVariant, Tag


class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1


class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1


@admin.register(Collection)
class CollectionAdmin(admin.ModelAdmin):
    list_display = ["name", "slug", "is_active", "order"]
    prepopulated_fields = {"slug": ("name",)}
    list_editable = ["is_active", "order"]


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ["name", "collection", "price", "is_active", "is_new_arrival", "is_best_seller", "created_at"]
    list_filter = ["collection", "is_active", "is_new_arrival", "is_best_seller"]
    search_fields = ["name", "slug", "description"]
    prepopulated_fields = {"slug": ("name",)}
    inlines = [ProductImageInline, ProductVariantInline]
    filter_horizontal = ["tags"]


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    prepopulated_fields = {"slug": ("name",)}
