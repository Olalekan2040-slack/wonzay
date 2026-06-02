from django.db import models


class AnnouncementBar(models.Model):
    message = models.CharField(max_length=300)
    coupon_code = models.CharField(max_length=50, blank=True)
    link_url = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.message[:60]


class HeroSlide(models.Model):
    background_image = models.ImageField(upload_to="hero/")
    headline = models.CharField(max_length=100)
    sub_headline = models.CharField(max_length=200, blank=True)
    cta1_label = models.CharField(max_length=50, default="Shop Now")
    cta1_url = models.CharField(max_length=200, default="/collections/")
    cta2_label = models.CharField(max_length=50, blank=True)
    cta2_url = models.CharField(max_length=200, blank=True)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.headline


class TrustBadge(models.Model):
    icon_class = models.CharField(max_length=100, blank=True, help_text="Heroicon name or custom SVG class")
    icon_svg = models.TextField(blank=True, help_text="Paste raw SVG markup")
    label = models.CharField(max_length=100)
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.label


class BrandStory(models.Model):
    image = models.ImageField(upload_to="brand/")
    heading = models.CharField(max_length=200)
    body = models.TextField()
    cta_label = models.CharField(max_length=50, default="Shop Now")
    cta_url = models.CharField(max_length=200, default="/collections/")

    def __str__(self):
        return self.heading
