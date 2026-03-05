from apps.catalog.models import Product, CanonicalProduct


def unify_products_by_mpn():
    products = Product.objects.exclude(mpn="").exclude(manufacturer="")

    for p in products:
        canonical, _ = CanonicalProduct.objects.get_or_create(
            manufacturer=p.manufacturer.lower().strip(),
            mpn=p.mpn.lower().strip(),
            defaults={
                "name": p.name,
                "category": p.category,
                "image_url": p.image_url,
            },
        )

        p.canonical = canonical
        p.save(update_fields=["canonical"])
