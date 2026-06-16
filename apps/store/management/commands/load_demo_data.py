"""
Management command: python manage.py load_demo_data

Populates the database with collections and products using images from
static/images/downloaded_images/, plus content blocks, pages, and shipping rates.
"""
import shutil
from pathlib import Path
from django.core.management.base import BaseCommand
from django.conf import settings
from django.core.files import File


STATIC_IMAGES = Path(settings.BASE_DIR) / "static" / "images" / "downloaded_images"


def _copy_to_media(src_path, dest_subdir):
    """Copy src_path into MEDIA_ROOT/dest_subdir and return a django File."""
    if not src_path.exists():
        return None
    dest_dir = Path(settings.MEDIA_ROOT) / dest_subdir
    dest_dir.mkdir(parents=True, exist_ok=True)
    dest = dest_dir / src_path.name
    if not dest.exists():
        shutil.copy2(src_path, dest)
    return dest


class Command(BaseCommand):
    help = "Load demo data for Wonzays Kollections"

    def handle(self, *args, **options):
        self._load_content()
        self._load_collections()
        self._load_products()
        self._load_static_pages()
        self._load_shipping_rates()
        self.stdout.write(self.style.SUCCESS("Demo data loaded successfully!"))

    # ------------------------------------------------------------------ #
    def _load_content(self):
        from apps.content.models import AnnouncementBar, HeroSlide, TrustBadge, BrandStory

        AnnouncementBar.objects.all().delete()
        AnnouncementBar.objects.create(
            message="🎉 UP TO 40% OFF NEW ARRIVALS — USE CODE: WONZAY40 AT CHECKOUT",
            coupon_code="WONZAY40", order=0, is_active=True,
        )
        AnnouncementBar.objects.create(
            message="FREE SHIPPING on orders over $150 Australia-wide",
            order=1, is_active=True,
        )

        HeroSlide.objects.all().delete()
        hero_src = STATIC_IMAGES / "store_lifestyle" / "store_lifestyle_001.jpg"
        if hero_src.exists():
            slide = HeroSlide(
                headline="Wear Your Story.",
                sub_headline="Contemporary African fashion — bold prints, effortless silhouettes. Ships from Queensland, Australia.",
                cta1_label="Shop New Arrivals", cta1_url="/collections/new-arrivals/",
                cta2_label="View Collections", cta2_url="/collections/",
                order=0, is_active=True,
            )
            with open(hero_src, "rb") as f:
                slide.background_image.save("hero1.jpg", File(f), save=True)
        else:
            self.stdout.write(self.style.WARNING("  Hero image not found — slide skipped."))

        TrustBadge.objects.all().delete()
        for i, label in enumerate(["African Fashion", "Ready to Wear", "Made in Nigeria", "Buy Now Pay Later"]):
            TrustBadge.objects.create(label=label, order=i, is_active=True)

        BrandStory.objects.all().delete()
        brand_src = STATIC_IMAGES / "store_lifestyle" / "store_lifestyle_002.jpg"
        story = BrandStory(
            heading="Rooted in culture, worn with pride.",
            body=(
                "Wonzays Kollections brings the vibrancy of African fashion to contemporary wardrobes "
                "across Australia and beyond.\n\nEvery piece tells a story — from the bold Ankara prints "
                "to the flowing kaftans. Our collections are designed for the modern woman who celebrates "
                "her heritage while embracing her individuality.\n\nHandpicked and curated with love from "
                "Karalee, Queensland."
            ),
            cta_label="Shop Collections", cta_url="/collections/",
        )
        if brand_src.exists():
            with open(brand_src, "rb") as f:
                story.image.save("brand_story.jpg", File(f), save=True)
        else:
            story.save()

        self.stdout.write("  Content blocks loaded")

    # ------------------------------------------------------------------ #
    def _load_collections(self):
        from apps.store.models import Collection

        Collection.objects.all().delete()

        lifestyle = STATIC_IMAGES / "store_lifestyle"
        women = STATIC_IMAGES / "women_clothing"
        men = STATIC_IMAGES / "men_clothing"
        acc = STATIC_IMAGES / "accessories"
        shoes = STATIC_IMAGES / "shoes"
        capes = STATIC_IMAGES / "capes_and_wraps"

        collections_data = [
            ("New Arrivals",   "new-arrivals",   "Just landed — fresh styles for the season.",              lifestyle / "store_lifestyle_003.jpg"),
            ("Women's Clothing","womens-clothing","Contemporary womenswear with an African edge.",           women / "women_clothing_001.jpg"),
            ("Men's Clothing", "mens-clothing",  "Bold menswear for the modern African gentleman.",         men / "men_clothing_001.jpg"),
            ("Accessories",    "accessories",    "Bags, jewellery and more to complete your look.",         acc / "accessories_001.jpg"),
            ("Shoes",          "shoes",          "Step out in style with our curated footwear collection.", shoes / "shoes_001.jpg"),
            ("Capes & Wraps",  "capes-and-wraps","Effortlessly elegant capes and wraps for every occasion.",capes / "capes_and_wraps_001.jpg"),
            ("Best Sellers",   "best-sellers",   "Our most loved pieces — customer favourites.",            lifestyle / "store_lifestyle_004.jpg"),
        ]

        for i, (name, slug, desc, img_path) in enumerate(collections_data):
            col = Collection(name=name, slug=slug, description=desc, is_active=True, order=i)
            if img_path.exists():
                with open(img_path, "rb") as f:
                    col.cover_image.save(f"col_{slug}.jpg", File(f), save=False)
            col.save()

        self.stdout.write("  Collections loaded")

    # ------------------------------------------------------------------ #
    def _load_products(self):
        from apps.store.models import Collection, Product, ProductImage, ProductVariant, Tag

        Product.objects.all().delete()
        Tag.objects.all().delete()

        women_col   = Collection.objects.get(slug="womens-clothing")
        men_col     = Collection.objects.get(slug="mens-clothing")
        acc_col     = Collection.objects.get(slug="accessories")
        shoes_col   = Collection.objects.get(slug="shoes")
        capes_col   = Collection.objects.get(slug="capes-and-wraps")
        new_col     = Collection.objects.get(slug="new-arrivals")
        best_col    = Collection.objects.get(slug="best-sellers")

        tag_names = ["new_arrival", "best_seller", "african_print", "kaftan", "dress", "jumpsuit", "set", "shoes", "accessories"]
        tags = {}
        for t in tag_names:
            obj, _ = Tag.objects.get_or_create(name=t, defaults={"slug": t.replace("_", "-")})
            tags[t] = obj

        w = STATIC_IMAGES / "women_clothing"
        m = STATIC_IMAGES / "men_clothing"
        a = STATIC_IMAGES / "accessories"
        s = STATIC_IMAGES / "shoes"
        c = STATIC_IMAGES / "capes_and_wraps"

        products_data = [
            # ---- WOMEN'S CLOTHING ----
            {
                "name": "Adunni Ankara Midi Dress",
                "collection": women_col,
                "price": "129.00", "compare_at_price": "179.00",
                "description": "A stunning midi dress featuring vibrant Ankara print. Crafted from premium wax cotton with a flattering A-line silhouette and side pockets. Perfect for brunch through to evening events.",
                "images": [w / "women_clothing_001.jpg", w / "women_clothing_002.jpg"],
                "sizes": ["XS", "S", "M", "L", "XL"],
                "colours": ["Blue/Gold Print", "Red/Black Print"],
                "tags": ["new_arrival", "african_print", "dress"],
                "is_new_arrival": True, "is_best_seller": False,
            },
            {
                "name": "Amira Ruched Bodycon Dress",
                "collection": women_col,
                "price": "95.00", "compare_at_price": None,
                "description": "A figure-hugging bodycon dress with ruched detailing and a rich African wax print. Features a midi length and wrap-style bodice — a statement piece for evenings out.",
                "images": [w / "women_clothing_003.jpg", w / "women_clothing_004.jpg"],
                "sizes": ["XS", "S", "M", "L", "XL"],
                "colours": ["Teal/Orange Print"],
                "tags": ["new_arrival", "dress"],
                "is_new_arrival": True, "is_best_seller": False,
            },
            {
                "name": "Zara Two-Piece Ankara Set",
                "collection": women_col,
                "price": "159.00", "compare_at_price": None,
                "description": "A luxurious two-piece set featuring a flowing top and matching trousers. Made from soft, breathable fabric with a bold geometric Ankara pattern. Available in multiple colour options.",
                "images": [w / "women_clothing_005.jpg", w / "women_clothing_006.jpeg"],
                "sizes": ["S", "M", "L", "XL", "XXL"],
                "colours": ["Purple/Gold", "Green/White"],
                "tags": ["new_arrival", "set"],
                "is_new_arrival": True, "is_best_seller": True,
            },
            {
                "name": "Kezia Kaftan Maxi Dress",
                "collection": women_col,
                "price": "89.00", "compare_at_price": "119.00",
                "description": "A flowy, elegant kaftan dress perfect for warm-weather occasions. Features a v-neck design with tassel trim and an all-over floral African wax print.",
                "images": [w / "women_clothing_007.png", w / "women_clothing_008.jpg"],
                "sizes": ["ONE SIZE", "L", "XL", "XXL"],
                "colours": ["Orange/Black", "Yellow/Green"],
                "tags": ["best_seller", "kaftan", "dress"],
                "is_new_arrival": False, "is_best_seller": True,
            },
            {
                "name": "Folake Wide-Leg Jumpsuit",
                "collection": women_col,
                "price": "119.00", "compare_at_price": None,
                "description": "A sophisticated wide-leg jumpsuit with bold African print. Features a halter neck, cinched waist and palazzo-style legs. A statement piece for any wardrobe.",
                "images": [w / "women_clothing_009.jpg", w / "women_clothing_010.png"],
                "sizes": ["XS", "S", "M", "L", "XL"],
                "colours": ["Multi-colour Print"],
                "tags": ["new_arrival", "jumpsuit"],
                "is_new_arrival": True, "is_best_seller": False,
            },
            {
                "name": "Nkechi African Print Blazer Set",
                "collection": new_col,
                "price": "175.00", "compare_at_price": "215.00",
                "description": "A power-dressing blazer and trouser set in vibrant Ankara print. Perfect for the workplace or special occasions. Tailored cut with single-button blazer and high-waist trousers.",
                "images": [w / "women_clothing_011.jpg", w / "women_clothing_012.jpg"],
                "sizes": ["S", "M", "L", "XL"],
                "colours": ["Blue Ankara", "Red Ankara"],
                "tags": ["best_seller", "set"],
                "is_new_arrival": False, "is_best_seller": True,
            },
            {
                "name": "Chisom Peplum Top & Skirt Set",
                "collection": women_col,
                "price": "145.00", "compare_at_price": "185.00",
                "description": "A chic peplum top paired with a matching midi skirt in rich Ankara fabric. The peplum silhouette flatters all body types, making it a versatile addition to any wardrobe.",
                "images": [w / "women_clothing_013.jpg", w / "women_clothing_014.jpg"],
                "sizes": ["XS", "S", "M", "L", "XL", "XXL"],
                "colours": ["Green/Gold", "Navy/Orange"],
                "tags": ["african_print", "set"],
                "is_new_arrival": True, "is_best_seller": False,
            },
            {
                "name": "Yetunde Ankara Wrap Dress",
                "collection": best_col,
                "price": "110.00", "compare_at_price": None,
                "description": "A timeless wrap dress in bold Ankara print. Adjustable tie waist for a flattering fit, with a midi-length hem and flutter sleeves. Easy to dress up or down.",
                "images": [w / "women_clothing_015.jpg", w / "women_clothing_016.jpg"],
                "sizes": ["S", "M", "L", "XL"],
                "colours": ["Mixed Print"],
                "tags": ["best_seller", "dress"],
                "is_new_arrival": False, "is_best_seller": True,
            },
            {
                "name": "Bimpe Floral Off-Shoulder Dress",
                "collection": women_col,
                "price": "99.00", "compare_at_price": "130.00",
                "description": "An eye-catching off-shoulder dress in a floral African wax print. Features an elasticated neckline, ruffle hem and a comfortable relaxed fit. Great for summer occasions.",
                "images": [w / "women_clothing_017.jpg", w / "women_clothing_018.jpg"],
                "sizes": ["XS", "S", "M", "L"],
                "colours": ["Floral Mix"],
                "tags": ["african_print", "dress"],
                "is_new_arrival": True, "is_best_seller": False,
            },
            {
                "name": "Sade Ankara Co-ord Set",
                "collection": new_col,
                "price": "165.00", "compare_at_price": None,
                "description": "A coordinated crop top and flared trousers set in striking Ankara fabric. Mix and match pieces or wear as a complete look. Features side pockets and a comfortable elasticated waist.",
                "images": [w / "women_clothing_019.jpg", w / "women_clothing_020.jpg"],
                "sizes": ["S", "M", "L", "XL"],
                "colours": ["Yellow/Blue Print", "Pink/Green Print"],
                "tags": ["new_arrival", "set"],
                "is_new_arrival": True, "is_best_seller": False,
            },

            # ---- MEN'S CLOTHING ----
            {
                "name": "Tunde Men's Agbada Set",
                "collection": men_col,
                "price": "199.00", "compare_at_price": "249.00",
                "description": "A regal three-piece Agbada set for the modern African gentleman. Includes embroidered top, trousers and flowing outer robe. Premium fabric with intricate hand-stitched detailing.",
                "images": [m / "men_clothing_001.jpg", m / "men_clothing_002.jpg"],
                "sizes": ["S", "M", "L", "XL", "XXL", "XXXL"],
                "colours": ["Royal Blue", "White/Gold", "Black"],
                "tags": ["new_arrival"],
                "is_new_arrival": True, "is_best_seller": False,
            },
            {
                "name": "Emeka Kaftan Top & Trouser Set",
                "collection": men_col,
                "price": "155.00", "compare_at_price": None,
                "description": "A sophisticated kaftan top and matching trouser set in premium cotton blend. Features subtle embroidery at the neckline and cuffs. Cool, breathable and elegant.",
                "images": [m / "men_clothing_003.jpg", m / "men_clothing_004.jpg"],
                "sizes": ["S", "M", "L", "XL", "XXL"],
                "colours": ["White", "Sky Blue", "Champagne"],
                "tags": ["best_seller", "kaftan"],
                "is_new_arrival": False, "is_best_seller": True,
            },
            {
                "name": "Chukwu Ankara Senator Set",
                "collection": men_col,
                "price": "179.00", "compare_at_price": "219.00",
                "description": "A distinguished senator-style two-piece featuring a long-sleeve Ankara top and matching trousers. A celebration of Nigerian menswear tradition crafted for the contemporary man.",
                "images": [m / "men_clothing_005.jpg", m / "men_clothing_006.jpg"],
                "sizes": ["M", "L", "XL", "XXL", "XXXL"],
                "colours": ["Brown/Gold Ankara", "Blue/White Ankara"],
                "tags": ["african_print"],
                "is_new_arrival": True, "is_best_seller": False,
            },
            {
                "name": "Obinna Embroidered Dashiki Top",
                "collection": men_col,
                "price": "75.00", "compare_at_price": None,
                "description": "A vibrant dashiki top with rich embroidered detailing at the neckline and cuffs. Made from lightweight breathable cotton — a wardrobe essential for any occasion.",
                "images": [m / "men_clothing_007.jpg", m / "men_clothing_008.jpg"],
                "sizes": ["S", "M", "L", "XL", "XXL"],
                "colours": ["Multi-colour"],
                "tags": ["african_print"],
                "is_new_arrival": False, "is_best_seller": True,
            },
            {
                "name": "Femi Classic Boubou Robe",
                "collection": best_col,
                "price": "215.00", "compare_at_price": "265.00",
                "description": "An elegant boubou robe in luxurious jacquard fabric. Wide sleeves, flowing silhouette, with intricate embroidery detail. A true statement piece for formal occasions.",
                "images": [m / "men_clothing_009.jpg", m / "men_clothing_010.jpg"],
                "sizes": ["M", "L", "XL", "XXL"],
                "colours": ["Ivory/Gold", "Black/Gold"],
                "tags": ["best_seller"],
                "is_new_arrival": False, "is_best_seller": True,
            },
            {
                "name": "Kola Linen Kaftan Shirt",
                "collection": men_col,
                "price": "85.00", "compare_at_price": None,
                "description": "A relaxed linen kaftan shirt with Ankara trim detailing. Perfect for casual days or beach occasions. Breathable fabric keeps you cool all day.",
                "images": [m / "men_clothing_011.jpg", m / "men_clothing_012.jpg"],
                "sizes": ["S", "M", "L", "XL"],
                "colours": ["White/Ankara Trim", "Navy/Ankara Trim"],
                "tags": ["african_print"],
                "is_new_arrival": True, "is_best_seller": False,
            },
            {
                "name": "Dayo Ankara Suit Set",
                "collection": new_col,
                "price": "245.00", "compare_at_price": "295.00",
                "description": "A striking two-piece suit in bold Ankara fabric. Features a tailored blazer with notch lapels and matching straight-cut trousers. Turn heads at any event.",
                "images": [m / "men_clothing_013.jpg", m / "men_clothing_014.png"],
                "sizes": ["S", "M", "L", "XL", "XXL"],
                "colours": ["Blue/Yellow Ankara"],
                "tags": ["new_arrival", "african_print"],
                "is_new_arrival": True, "is_best_seller": False,
            },

            # ---- ACCESSORIES ----
            {
                "name": "Ade Woven Tote Bag",
                "collection": acc_col,
                "price": "65.00", "compare_at_price": None,
                "description": "A beautifully handwoven tote bag inspired by traditional African weaving techniques. Spacious interior with zip pocket and magnetic closure. Fully lined.",
                "images": [a / "accessories_001.jpg", a / "accessories_002.jpg"],
                "sizes": ["ONE SIZE"],
                "colours": ["Natural Brown", "Black"],
                "tags": ["best_seller", "accessories"],
                "is_new_arrival": False, "is_best_seller": True,
            },
            {
                "name": "Afua Beaded Statement Necklace",
                "collection": acc_col,
                "price": "45.00", "compare_at_price": "60.00",
                "description": "A bold beaded necklace inspired by traditional African jewellery. Handcrafted with colourful glass and wooden beads. A perfect finishing touch for any outfit.",
                "images": [a / "accessories_003.jpg", a / "accessories_004.jpg"],
                "sizes": ["ONE SIZE"],
                "colours": ["Multi-colour", "Earth Tones"],
                "tags": ["new_arrival", "accessories"],
                "is_new_arrival": True, "is_best_seller": False,
            },
            {
                "name": "Nneka Ankara Clutch Bag",
                "collection": acc_col,
                "price": "55.00", "compare_at_price": None,
                "description": "An elegant clutch bag crafted from rich Ankara fabric with a structured frame. Features a magnetic snap closure and detachable chain strap. The perfect evening companion.",
                "images": [a / "accessories_005.jpg", a / "accessories_006.jpeg"],
                "sizes": ["ONE SIZE"],
                "colours": ["Mixed Ankara Print"],
                "tags": ["accessories"],
                "is_new_arrival": True, "is_best_seller": False,
            },
            {
                "name": "Amaka Ankara Hoop Earrings",
                "collection": acc_col,
                "price": "28.00", "compare_at_price": None,
                "description": "Lightweight hoop earrings covered in vibrant Ankara fabric. Hypoallergenic posts, comfortable for all-day wear. A pop of colour for any look.",
                "images": [a / "accessories_007.jpg", a / "accessories_008.jpg"],
                "sizes": ["ONE SIZE"],
                "colours": ["Assorted Prints"],
                "tags": ["accessories"],
                "is_new_arrival": False, "is_best_seller": True,
            },
            {
                "name": "Ifeoma Kente Crossbody Bag",
                "collection": best_col,
                "price": "79.00", "compare_at_price": "99.00",
                "description": "A stylish crossbody bag woven from authentic Kente-inspired fabric. Features an adjustable strap, multiple pockets and a secure zip closure.",
                "images": [a / "accessories_009.jpeg", a / "accessories_010.jpg"],
                "sizes": ["ONE SIZE"],
                "colours": ["Gold/Green Kente", "Red/Blue Kente"],
                "tags": ["best_seller", "accessories"],
                "is_new_arrival": False, "is_best_seller": True,
            },

            # ---- SHOES ----
            {
                "name": "Remi Ankara Wedge Heels",
                "collection": shoes_col,
                "price": "95.00", "compare_at_price": "120.00",
                "description": "Stunning wedge heels wrapped in vibrant Ankara fabric. Cushioned insole for comfort, with a 7cm wedge and ankle strap for security. A true statement shoe.",
                "images": [s / "shoes_001.jpg", s / "shoes_002.jpg"],
                "sizes": ["6", "8", "10", "12", "14"],
                "colours": ["Blue Ankara", "Red Ankara"],
                "tags": ["new_arrival", "shoes"],
                "is_new_arrival": True, "is_best_seller": False,
            },
            {
                "name": "Toyin Block Heel Sandals",
                "collection": shoes_col,
                "price": "85.00", "compare_at_price": None,
                "description": "Elegant block heel sandals with Ankara fabric straps and a sturdy 6cm heel. Open-toe design with cushioned footbed for all-day comfort.",
                "images": [s / "shoes_003.jpg", s / "shoes_004.jpg"],
                "sizes": ["6", "8", "10", "12", "14"],
                "colours": ["Mixed Print"],
                "tags": ["best_seller", "shoes"],
                "is_new_arrival": False, "is_best_seller": True,
            },
            {
                "name": "Ngozi Flat Ankara Mules",
                "collection": shoes_col,
                "price": "69.00", "compare_at_price": "89.00",
                "description": "Chic slip-on mules featuring Ankara fabric uppers and a comfortable flat sole. Versatile enough for casual days or dressed-up occasions.",
                "images": [s / "shoes_005.jpg", s / "shoes_006.jpg"],
                "sizes": ["6", "8", "10", "12"],
                "colours": ["Yellow/Green Ankara"],
                "tags": ["shoes"],
                "is_new_arrival": True, "is_best_seller": False,
            },
            {
                "name": "Adaeze Embellished Kitten Heels",
                "collection": best_col,
                "price": "110.00", "compare_at_price": None,
                "description": "Delicate kitten heels adorned with hand-sewn African beadwork on the straps. A refined, feminine shoe that adds a touch of African elegance to any ensemble.",
                "images": [s / "shoes_007.jpg", s / "shoes_008.jpg"],
                "sizes": ["6", "8", "10", "12", "14"],
                "colours": ["Ivory/Gold", "Black/Silver"],
                "tags": ["best_seller", "shoes"],
                "is_new_arrival": False, "is_best_seller": True,
            },
            {
                "name": "Funke Platform Sneakers",
                "collection": shoes_col,
                "price": "79.00", "compare_at_price": None,
                "description": "Contemporary platform sneakers with Ankara fabric panels. Chunky sole for added height and comfort. A fusion of street style and African fashion heritage.",
                "images": [s / "shoes_009.jpg", s / "shoes_010.jpg"],
                "sizes": ["6", "8", "10", "12"],
                "colours": ["White/Ankara"],
                "tags": ["new_arrival", "shoes"],
                "is_new_arrival": True, "is_best_seller": False,
            },
            {
                "name": "Kemi Leather Ankle Boots",
                "collection": new_col,
                "price": "145.00", "compare_at_price": "175.00",
                "description": "Sleek ankle boots crafted from vegan leather with Ankara fabric trim at the cuff. Side zip closure and low block heel. Polished enough for work, edgy enough for evenings.",
                "images": [s / "shoes_011.jpg", s / "shoes_012.jpg"],
                "sizes": ["6", "8", "10", "12"],
                "colours": ["Black", "Tan"],
                "tags": ["new_arrival", "shoes"],
                "is_new_arrival": True, "is_best_seller": False,
            },

            # ---- CAPES & WRAPS ----
            {
                "name": "Obiageli Ankara Cape",
                "collection": capes_col,
                "price": "89.00", "compare_at_price": "115.00",
                "description": "A dramatic floor-length cape in vivid Ankara wax print. Fully lined with a satin interior for a luxurious feel. Effortlessly transforms any outfit into a showstopper.",
                "images": [c / "capes_and_wraps_001.jpg", c / "capes_and_wraps_002.jpg"],
                "sizes": ["ONE SIZE"],
                "colours": ["Blue/Gold Print", "Red/Black Print"],
                "tags": ["new_arrival", "african_print"],
                "is_new_arrival": True, "is_best_seller": False,
            },
            {
                "name": "Ogechi Sheer Wrap Skirt",
                "collection": capes_col,
                "price": "59.00", "compare_at_price": None,
                "description": "A versatile sheer wrap skirt in a lightweight African print chiffon. Can be worn as a pareo, wrap skirt or beach cover-up. One size fits all with adjustable tie waist.",
                "images": [c / "capes_and_wraps_003.jpg", c / "capes_and_wraps_004.jpg"],
                "sizes": ["ONE SIZE"],
                "colours": ["Teal Print", "Orange Print"],
                "tags": ["best_seller"],
                "is_new_arrival": False, "is_best_seller": True,
            },
            {
                "name": "Ugomma Embroidered Evening Cape",
                "collection": best_col,
                "price": "125.00", "compare_at_price": "155.00",
                "description": "An exquisite evening cape with hand-embroidered floral motifs on rich dupioni silk. Fastens at the neckline with a decorative brooch. The ultimate special-occasion statement.",
                "images": [c / "capes_and_wraps_005.jpg", c / "capes_and_wraps_006.jpg"],
                "sizes": ["ONE SIZE"],
                "colours": ["Black/Gold", "Burgundy/Silver"],
                "tags": ["best_seller", "african_print"],
                "is_new_arrival": False, "is_best_seller": True,
            },
            {
                "name": "Chinwe Ankara Shoulder Wrap",
                "collection": capes_col,
                "price": "49.00", "compare_at_price": None,
                "description": "A stylish shoulder wrap in vivid Ankara cotton. Drapes beautifully over the shoulders and can be pinned or knotted to stay in place. A quick way to elevate any look.",
                "images": [c / "capes_and_wraps_007.jpg", c / "capes_and_wraps_008.jpg"],
                "sizes": ["ONE SIZE"],
                "colours": ["Assorted Prints"],
                "tags": ["african_print"],
                "is_new_arrival": True, "is_best_seller": False,
            },
            {
                "name": "Ifunanya Kimono Wrap Cardigan",
                "collection": new_col,
                "price": "75.00", "compare_at_price": "95.00",
                "description": "A flowing kimono-style cardigan in lightweight African batik fabric. Open-front design with wide sleeves — perfect layered over a simple outfit for an instant style upgrade.",
                "images": [c / "capes_and_wraps_009.jpg", c / "capes_and_wraps_010.jpg"],
                "sizes": ["ONE SIZE"],
                "colours": ["Blue Batik", "Orange Batik"],
                "tags": ["new_arrival"],
                "is_new_arrival": True, "is_best_seller": False,
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

            for idx, img_path in enumerate(prod_data["images"]):
                if img_path.exists():
                    pi = ProductImage(
                        product=product,
                        alt_text=f"{product.name} view {idx + 1}",
                        order=idx,
                        is_primary=(idx == 0),
                    )
                    with open(img_path, "rb") as f:
                        pi.image.save(f"prod_{slug}_{idx}{img_path.suffix}", File(f), save=True)
                else:
                    self.stdout.write(self.style.WARNING(f"  Missing image: {img_path}"))

            sku_base = slug[:8].upper().replace("-", "")
            colours = prod_data.get("colours", [""])
            sizes = prod_data.get("sizes", ["ONE SIZE"])
            idx = 0
            for colour in colours:
                for size in sizes:
                    sku = f"{sku_base}-{colour[:3].upper()}-{size}-{idx:03d}"
                    ProductVariant.objects.create(
                        product=product,
                        size=size,
                        colour=colour,
                        sku=sku,
                        stock_quantity=10,
                        is_available=True,
                    )
                    idx += 1

        self.stdout.write(f"  {len(products_data)} products loaded")

    # ------------------------------------------------------------------ #
    def _load_static_pages(self):
        from apps.pages.models import StaticPage

        StaticPage.objects.all().delete()
        pages = [
            ("About Us", "about",
             "Wonzays Kollections is an Australian-based fashion retailer selling contemporary African clothing and accessories.\n\nFounded with a passion for celebrating African culture through fashion, we bring the vibrancy and artistry of African textile traditions to modern wardrobes around the world.\n\nBased in Karalee, Ipswich, Queensland, we ship Australia-wide and internationally. Every piece in our collection is handpicked for quality, style and cultural authenticity."),
            ("Shipping & Delivery", "shipping-delivery",
             "Standard Shipping: 3–7 business days — $10.00 AUD\nExpress Shipping: 1–3 business days — $20.00 AUD\nFree Standard Shipping on orders over $150 AUD\n\nWe ship Australia-wide and internationally. International orders may be subject to customs duties.\n\nAll orders are processed within 1–2 business days. You will receive a tracking number once your order has been dispatched."),
            ("Returns & Exchange", "returns-exchange",
             "We accept returns within 14 days of delivery.\n\nItems must be:\n- Unworn and unwashed\n- In their original condition with tags attached\n- Free from perfume, marks or damage\n\nTo arrange a return, please contact us at olalekanquadri58@gmail.com with your order number.\n\nExchanges are processed once we receive the returned item. Shipping costs for returns are at the customer's expense unless the item is faulty."),
            ("Size Chart", "size-chart",
             "SIZE GUIDE\n\nXS — Bust: 82cm, Waist: 64cm, Hip: 88cm\nS  — Bust: 86cm, Waist: 68cm, Hip: 92cm\nM  — Bust: 90cm, Waist: 72cm, Hip: 96cm\nL  — Bust: 96cm, Waist: 78cm, Hip: 102cm\nXL — Bust: 102cm, Waist: 84cm, Hip: 108cm\nXXL — Bust: 108cm, Waist: 90cm, Hip: 114cm\n\nMeasurements are in centimetres. If you are between sizes, we recommend sizing up for a more comfortable fit."),
        ]
        for title, slug, body in pages:
            StaticPage.objects.create(title=title, slug=slug, body=body, is_active=True)

        self.stdout.write("  Static pages loaded")

    # ------------------------------------------------------------------ #
    def _load_shipping_rates(self):
        from apps.orders.models import ShippingRate

        ShippingRate.objects.all().delete()
        ShippingRate.objects.create(name="Standard Shipping", country_code="AU", rate="10.00", estimated_days_min=3, estimated_days_max=7, is_active=True)
        ShippingRate.objects.create(name="Express Shipping", country_code="AU", rate="20.00", estimated_days_min=1, estimated_days_max=3, is_active=True)
        ShippingRate.objects.create(name="Free Shipping (Orders $150+)", country_code="AU", rate="0.00", estimated_days_min=3, estimated_days_max=7, is_active=True)

        self.stdout.write("  Shipping rates loaded")
