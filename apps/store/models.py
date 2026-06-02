from django.db import models
from django.utils.text import slugify
from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill
import datetime


class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Collection(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to="collections/", blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)
    meta_title = models.CharField(max_length=60, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)

    class Meta:
        ordering = ["order", "name"]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse("store:collection_detail", kwargs={"slug": self.slug})


class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True, db_index=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    compare_at_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    collection = models.ForeignKey(Collection, on_delete=models.SET_NULL, null=True, related_name="products")
    tags = models.ManyToManyField(Tag, blank=True)
    is_active = models.BooleanField(default=True)
    is_new_arrival = models.BooleanField(default=False)
    is_best_seller = models.BooleanField(default=False)
    meta_title = models.CharField(max_length=60, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [
            models.Index(fields=["slug"]),
            models.Index(fields=["collection"]),
        ]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse("store:product_detail", kwargs={"slug": self.slug})

    @property
    def is_on_sale(self):
        return self.compare_at_price and self.compare_at_price > self.price

    @property
    def discount_percentage(self):
        if self.is_on_sale:
            return int(((self.compare_at_price - self.price) / self.compare_at_price) * 100)
        return 0

    @property
    def is_new(self):
        return (
            self.is_new_arrival
            or (datetime.date.today() - self.created_at.date()).days <= 14
        )

    @property
    def primary_image(self):
        return self.images.filter(is_primary=True).first() or self.images.first()

    @property
    def secondary_image(self):
        images = list(self.images.all())
        if len(images) >= 2:
            return images[1]
        return None

    @property
    def average_rating(self):
        reviews = self.reviews.filter(is_approved=True)
        if reviews.exists():
            return reviews.aggregate(models.Avg("rating"))["rating__avg"]
        return None

    @property
    def review_count(self):
        return self.reviews.filter(is_approved=True).count()

    @property
    def in_stock(self):
        return self.variants.filter(is_available=True, stock_quantity__gt=0).exists()


class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="images")
    image = models.ImageField(upload_to="products/")
    alt_text = models.CharField(max_length=200)
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    thumbnail = ImageSpecField(
        source="image",
        processors=[ResizeToFill(400, 533)],
        format="WEBP",
        options={"quality": 85},
    )

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return f"{self.product.name} image {self.order}"


class ProductVariant(models.Model):
    SIZE_CHOICES = [
        ("XS", "XS"), ("S", "S"), ("M", "M"), ("L", "L"),
        ("XL", "XL"), ("XXL", "XXL"), ("XXXL", "XXXL"),
        ("ONE SIZE", "One Size"),
        ("6", "6"), ("8", "8"), ("10", "10"), ("12", "12"),
        ("14", "14"), ("16", "16"), ("18", "18"),
    ]

    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name="variants")
    size = models.CharField(max_length=20, blank=True)
    colour = models.CharField(max_length=50, blank=True)
    sku = models.CharField(max_length=100, unique=True)
    stock_quantity = models.PositiveIntegerField(default=0)
    is_available = models.BooleanField(default=True)

    class Meta:
        ordering = ["size", "colour"]

    def __str__(self):
        parts = [self.product.name]
        if self.size:
            parts.append(self.size)
        if self.colour:
            parts.append(self.colour)
        return " – ".join(parts)

    @property
    def stock_status(self):
        if not self.is_available or self.stock_quantity == 0:
            return "sold_out"
        if self.stock_quantity <= 3:
            return "low_stock"
        return "in_stock"
