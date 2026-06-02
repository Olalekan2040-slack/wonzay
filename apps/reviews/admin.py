from django.contrib import admin
from .models import Review, ReviewImage


class ReviewImageInline(admin.TabularInline):
    model = ReviewImage
    extra = 0


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ["product", "author", "rating", "is_approved", "is_featured", "created_at"]
    list_editable = ["is_approved", "is_featured"]
    list_filter = ["is_approved", "rating"]
    search_fields = ["product__name", "author__email", "title"]
    inlines = [ReviewImageInline]
