"""
Management command: python manage.py load_demo_data

Populates the database with sample collections, products using the
images from media/products/, hero slide, trust badges, brand story,
announcement bar, and static pages.
"""
import shutil
import uuid
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files import File


class Command(BaseCommand):
    help = "Load demo data for Wonzays Kollections"

    def handle(self, *args, **options):
        self._load_content()
        self._load_collections()
        self._load_products()
        self._load_static_pages()
        self._load_shipping_rates()
        self.stdout.write(self.style.SUCCESS("OK Demo data loaded successfully!"))

    def _img(self, src_name, dest_dir):
        """Copy an image from media/products/ and return a File object."""
        src = Path(settings.MEDIA_ROOT) / "products" / src_name
        if not src.exists():
            return None
        dest = Path(settings.MEDIA_ROOT) / dest_dir
        dest.mkdir(parents=True, exist_ok=True)
        dst = dest / src_name
        if not dst.exists():
            shutil.copy2(src, dst)
        return str(dest_dir / Path(src_name))

    def _load_content(self):
        from apps.content.models import AnnouncementBar, HeroSlide, TrustBadge, BrandStory

        AnnouncementBar.objects.all().delete()
        AnnouncementBar.objects.create(message="🎉 UP TO 40% OFF NEW ARRIVALS — USE CODE: WONZAY40 AT CHECKOUT", coupon_code="WONZAY40", order=0, is_active=True)
        AnnouncementBar.objects.create(message="FREE SHIPPING on orders over $150 Australia-wide", order=1, is_active=True)

        HeroSlide.objects.all().delete()
        hero_img_src = Path(settings.MEDIA_ROOT) / "hero" / "hero1.png"
        if hero_img_src.exists():
            slide = HeroSlide(headline="Wear Your Story.", sub_headline="Contemporary African fashion — bold prints, effortless silhouettes. Ships from Queensland, Australia.", cta1_label="Shop New Arrivals", cta1_url="/collections/new-arrivals/", cta2_label="View Collections", cta2_url="/collections/", order=0, is_active=True)
            with open(hero_img_src, "rb") as f:
                slide.background_image.save("hero1.png", File(f), save=True)
        else:
            self.stdout.write(self.style.WARNING("  Hero image not found — slide skipped."))

        TrustBadge.objects.all().delete()
        for i, label in enumerate(["African Fashion", "Ready to Wear", "Made in Nigeria", "Buy Now Pay Later"]):
            TrustBadge.objects.create(label=label, order=i, is_active=True)

        BrandStory.objects.all().delete()
        brand_img = Path(settings.MEDIA_ROOT) / "brand" / "brand_story.png"
        if brand_img.exists():
            story = BrandStory(heading="Rooted in culture, worn with pride.", body="Wonzays Kollections brings the vibrancy of African fashion to contemporary wardrobes across Australia and beyond.\n\nEvery piece tells a story — from the bold Ankara prints to the flowing kaftans. Our collections are designed for the modern woman who celebrates her heritage while embracing her individuality.\n\nHandpicked and curated with love from Karalee, Queensland.", cta_label="Shop Collections", cta_url="/collections/")
            with open(brand_img, "rb") as f:
                story.image.save("brand_story.png", File(f), save=True)
        else:
            BrandStory.objects.create(heading="Rooted in culture, worn with pride.", body="Wonzays Kollections brings the vibrancy of African fashion to contemporary wardrobes across Australia and beyond.\n\nEvery piece tells a story.", image="", cta_label="Shop Collections", cta_url="/collections/")

        self.stdout.write("  OK Content blocks loaded")

    def _load_collections(self):
        from apps.store.models import Collection

        Collection.objects.all().delete()
        collections_data = [
            ("New Arrivals", "new-arrivals", "Just landed — fresh styles for the season.", "image3.png"),
            ("Dresses", "dresses", "From casual day dresses to stunning evening gowns.", "image1.png"),
            ("Sets", "sets", "Perfectly coordinated two and three-piece sets.", "image2.png"),
            ("Tops", "tops", "Statement tops for every occasion.", "image4.png"),
            ("Jumpsuits", "jumpsuits", "One-piece wonders for effortless style.", "image5.png"),
            ("Men", "men", "Contemporary menswear with an African edge.", "image6.png"),
            ("Accessories", "accessories", "Bags, jewellery and more to complete your look.", "bag1.png"),
            ("Best Sellers", "best-sellers", "Our most loved pieces — customer favourites.", "image7.png"),
        ]
        media_products = Path(settings.MEDIA_ROOT) / "products"

        for i, (name, slug, desc, img_name) in enumerate(collections_data):
            col = Collection(name=name, slug=slug, description=desc, is_active=True, order=i)
            img_path = media_products / img_name
            if img_path.exists():
                with open(img_path, "rb") as f:
                    col.cover_image.save(f"col_{slug}.png", File(f), save=False)
            col.save()

        self.stdout.write("  OK Collections loaded")

    def _load_products(self):
        from apps.store.models import Collection, Product, ProductImage, ProductVariant, Tag

        Product.objects.all().delete()
        Tag.objects.all().delete()

        media_products = Path(settings.MEDIA_ROOT) / "products"

        tags = {}
        for t in ["new_arrival", "best_seller", "african_print", "kaftan", "dress", "jumpsuit", "set", "bag"]:
            tag, _ = Tag.objects.get_or_create(name=t, defaults={"slug": t.replace("_", "-")})
            tags[t] = tag

        dresses_col = Collection.objects.get(slug="dresses")
        sets_col = Collection.objects.get(slug="sets")
        new_col = Collection.objects.get(slug="new-arrivals")
        jumpsuits_col = Collection.objects.get(slug="jumpsuits")
        accessories_col = Collection.objects.get(slug="accessories")
        men_col = Collection.objects.get(slug="men")
        best_col = Collection.objects.get(slug="best-sellers")

        products_data = [
            {
                "name": "Adunni Ankara Midi Dress",
                "collection": dresses_col,
                "price": "129.00", "compare_at_price": "179.00",
                "description": "A stunning midi dress featuring vibrant Ankara print. Crafted from premium wax cotton, this piece features a flattering A-line silhouette and side pockets. Perfect for any occasion from brunch to evening events.",
                "images": ["image1.png", "image2.png"],
                "sizes": ["XS", "S", "M", "L", "XL"],
                "colours": ["Blue/Gold Print", "Red/Black Print"],
                "tags": ["new_arrival", "african_print", "dress"],
                "is_new_arrival": True, "is_best_seller": False,
            },
            {
                "name": "Zara Two-Piece Bubu Set",
                "collection": sets_col,
                "price": "159.00", "compare_at_price": None,
                "description": "A luxurious two-piece Bubu set featuring a flowing top and matching trousers. Made from soft, breathable fabric with a bold geometric Ankara pattern. Available in multiple colour options.",
                "images": ["image3.png", "image4.png"],
                "sizes": ["S", "M", "L", "XL", "XXL"],
                "colours": ["Purple/Gold", "Green/White"],
                "tags": ["new_arrival", "set"],
                "is_new_arrival": True, "is_best_seller": True,
            },
            {
                "name": "Kezia Kaftan Dress",
                "collection": dresses_col,
                "price": "89.00", "compare_at_price": "119.00",
                "description": "A flowy, elegant kaftan dress perfect for warm-weather occasions. Features a v-neck design with tassel trim and an all-over floral African wax print.",
                "images": ["image5.png", "image6.png"],
                "sizes": ["ONE SIZE", "L", "XL", "XXL"],
                "colours": ["Orange/Black", "Yellow/Green"],
                "tags": ["best_seller", "kaftan", "dress"],
                "is_new_arrival": False, "is_best_seller": True,
            },
            {
                "name": "Folake Jumpsuit",
                "collection": jumpsuits_col,
                "price": "119.00", "compare_at_price": None,
                "description": "A sophisticated wide-leg jumpsuit with bold African print. Features a halter neck, cinched waist and wide palazzo-style legs. A statement piece for any wardrobe.",
                "images": ["image7.png", "image8.png"],
                "sizes": ["XS", "S", "M", "L", "XL"],
                "colours": ["Multi-colour Print"],
                "tags": ["new_arrival", "jumpsuit"],
                "is_new_arrival": True, "is_best_seller": False,
            },
            {
                "name": "Ade Woven Tote Bag",
                "collection": accessories_col,
                "price": "65.00", "compare_at_price": None,
                "description": "A beautifully handwoven tote bag inspired by traditional African weaving techniques. Spacious interior with zip pocket and magnetic closure. Fully lined.",
                "images": ["bag1.png", "bag2.png"],
                "sizes": ["ONE SIZE"],
                "colours": ["Natural Brown", "Black"],
                "tags": ["best_seller", "bag"],
                "is_new_arrival": False, "is_best_seller": True,
            },
            {
                "name": "Tunde Men's Agbada Set",
                "collection": men_col,
                "price": "199.00", "compare_at_price": "249.00",
                "description": "A regal three-piece Agbada set for the modern African gentleman. Includes embroidered top, trousers and flowing outer robe. Premium fabric with intricate hand-stitched detailing.",
                "images": ["image9.png", "image10.png"],
                "sizes": ["S", "M", "L", "XL", "XXL", "XXXL"],
                "colours": ["Royal Blue", "White/Gold", "Black"],
                "tags": ["new_arrival"],
                "is_new_arrival": True, "is_best_seller": False,
            },
            {
                "name": "Amira Ruched Bodycon Dress",
                "collection": new_col,
                "price": "95.00", "compare_at_price": None,
                "description": "A figure-hugging bodycon dress with ruched detailing and a rich African wax print. Features a midi length and wrap-style bodice. Perfect for evenings out.",
                "images": ["image12.png", "image1.png"],
                "sizes": ["XS", "S", "M", "L", "XL"],
                "colours": ["Teal/Orange Print"],
                "tags": ["new_arrival", "dress"],
                "is_new_arrival": True, "is_best_seller": False,
            },
            {
                "name": "Nkechi African Print Blazer Set",
                "collection": sets_col,
                "price": "175.00", "compare_at_price": "215.00",
                "description": "A power-dressing blazer and trouser set in vibrant Ankara print. Perfect for the workplace or special occasions. Tailored cut with single-button blazer and high-waist trousers.",
                "images": ["image2.png", "image3.png"],
                "sizes": ["S", "M", "L", "XL"],
                "colours": ["Blue Ankara", "Red Ankara"],
                "tags": ["best_seller"],
                "is_new_arrival": False, "is_best_seller": True,
            },
        ]

        for prod_data in products_data:
            slug = prod_data["name"].lower().replace(" ", "-").replace("'", "")
            slug = "".join(c for c in slug if c.isalnum() or c == "-")

            product = Product(
                name=prod_data["name"],
                slug=slug,
                description=prod_data["description"],
                price=prod_data["price"],
                compare_at_price=prod_data.get("compare_at_price"),
                collection=prod_data["collection"],
                is_active=True,
                is_new_arrival=prod_data["is_new_arrival"],
                is_best_seller=prod_data["is_best_seller"],
            )
            product.save()

            for tag_name in prod_data["tags"]:
                if tag_name in tags:
                    product.tags.add(tags[tag_name])

            # Product images
            for idx, img_name in enumerate(prod_data["images"]):
                img_path = media_products / img_name
                if img_path.exists():
                    pi = ProductImage(product=product, alt_text=f"{product.name} view {idx+1}", order=idx, is_primary=(idx == 0))
                    with open(img_path, "rb") as f:
                        pi.image.save(f"prod_{slug}_{idx}.png", File(f), save=True)

            # Variants
            sku_base = slug[:8].upper().replace("-", "")
            colours = prod_data.get("colours", [""])
            sizes = prod_data.get("sizes", ["ONE SIZE"])
            variant_idx = 0
            for colour in colours:
                for size in sizes:
                    sku = f"{sku_base}-{colour[:3].upper()}-{size}-{variant_idx:03d}"
                    ProductVariant.objects.create(
                        product=product,
                        size=size,
                        colour=colour,
                        sku=sku,
                        stock_quantity=10,
                        is_available=True,
                    )
                    variant_idx += 1

        self.stdout.write("  OK Products loaded")

    def _load_static_pages(self):
        from apps.pages.models import StaticPage

        StaticPage.objects.all().delete()
        pages = [
            ("About Us", "about", "Wonzays Kollections is an Australian-based fashion retailer selling contemporary African clothing and accessories.\n\nFounded with a passion for celebrating African culture through fashion, we bring the vibrancy and artistry of African textile traditions to modern wardrobes around the world.\n\nBased in Karalee, Ipswich, Queensland, we ship Australia-wide and internationally. Every piece in our collection is handpicked for quality, style and cultural authenticity."),
            ("Shipping & Delivery", "shipping-delivery", "Standard Shipping: 3–7 business days — $10.00 AUD\nExpress Shipping: 1–3 business days — $20.00 AUD\nFree Standard Shipping on orders over $150 AUD\n\nWe ship Australia-wide and internationally. International orders may be subject to customs duties.\n\nAll orders are processed within 1–2 business days. You will receive a tracking number once your order has been dispatched."),
            ("Returns & Exchange", "returns-exchange", "We accept returns within 14 days of delivery.\n\nItems must be:\n- Unworn and unwashed\n- In their original condition with tags attached\n- Free from perfume, marks or damage\n\nTo arrange a return, please contact us at olalekanquadri58@gmail.com with your order number.\n\nExchanges are processed once we receive the returned item. Shipping costs for returns are at the customer's expense unless the item is faulty."),
            ("Size Chart", "size-chart", "SIZE GUIDE\n\nXS — Bust: 82cm, Waist: 64cm, Hip: 88cm\nS  — Bust: 86cm, Waist: 68cm, Hip: 92cm\nM  — Bust: 90cm, Waist: 72cm, Hip: 96cm\nL  — Bust: 96cm, Waist: 78cm, Hip: 102cm\nXL — Bust: 102cm, Waist: 84cm, Hip: 108cm\nXXL — Bust: 108cm, Waist: 90cm, Hip: 114cm\n\nMeasurements are in centimetres. If you are between sizes, we recommend sizing up for a more comfortable fit.\n\nAll measurements are approximate and may vary slightly between styles."),
        ]
        for title, slug, body in pages:
            StaticPage.objects.create(title=title, slug=slug, body=body, is_active=True)

        self.stdout.write("  OK Static pages loaded")

    def _load_shipping_rates(self):
        from apps.orders.models import ShippingRate

        ShippingRate.objects.all().delete()
        ShippingRate.objects.create(name="Standard Shipping", country_code="AU", rate="10.00", estimated_days_min=3, estimated_days_max=7, is_active=True)
        ShippingRate.objects.create(name="Express Shipping", country_code="AU", rate="20.00", estimated_days_min=1, estimated_days_max=3, is_active=True)
        ShippingRate.objects.create(name="Free Shipping (Orders $150+)", country_code="AU", rate="0.00", estimated_days_min=3, estimated_days_max=7, is_active=True)

        self.stdout.write("  OK Shipping rates loaded")
