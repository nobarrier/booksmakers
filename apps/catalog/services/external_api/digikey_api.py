import os
import requests
from dotenv import load_dotenv
from pathlib import Path
from .digikey_auth import get_access_token

BASE_DIR = Path(__file__).resolve().parents[4]
load_dotenv(BASE_DIR / ".env")

CLIENT_ID = os.getenv("DIGIKEY_CLIENT_ID")
ENV = os.getenv("DIGIKEY_ENV")

if ENV == "sandbox":
    BASE_URL = "https://sandbox-api.digikey.com"
else:
    BASE_URL = "https://api.digikey.com"


def search_products(keyword="Raspberry Pi"):
    token = get_access_token()

    url = f"{BASE_URL}/products/v4/search/keyword"

    headers = {
        "Authorization": f"Bearer {token}",
        "X-DIGIKEY-Client-Id": CLIENT_ID,
        "Content-Type": "application/json",
        "Accept": "application/json",
    }

    payload = {
        "Keywords": keyword,
        "RecordCount": 5,
    }

    response = requests.post(url, json=payload, headers=headers)

    if response.status_code != 200:
        raise Exception(response.text)

    return response.json()


def normalize_products(data):
    products = []

    # Digikey 응답 구조 대응
    if "Products" in data:
        product_list = data.get("Products", [])
    elif "ProductSearchResults" in data:
        product_list = data["ProductSearchResults"].get("Products", [])
    else:
        product_list = []

    for item in product_list:

        # 이미지
        image_url = (
            item.get("ImageUrl")
            or item.get("PhotoUrl")
            or item.get("PrimaryPhoto", {}).get("MediumPhotoUrl")
            or item.get("PrimaryPhoto", {}).get("SmallPhotoUrl")
        )

        # Variations
        variations = item.get("ProductVariations", [])

        # Digikey Part Number
        dk_part = (
            item.get("DigiKeyProductNumber")
            or item.get("DigiKeyPartNumber")
            or (variations[0].get("DigiKeyProductNumber") if variations else None)
        )

        # 🔥 Manufacturer
        manufacturer = None
        if item.get("Manufacturer"):
            manufacturer = item.get("Manufacturer", {}).get("Name")

        # 🔥 진짜 MPN
        mpn = item.get("ManufacturerProductNumber")

        # fallback
        if not mpn:
            mpn = dk_part

        # Category Path
        category_path = []

        if item.get("Category"):

            category = item.get("Category")

            while category:
                category_path.insert(0, category.get("Name"))
                category = category.get("Parent")

        products.append(
            {
                "manufacturer": manufacturer,
                "mpn": mpn,
                "dk_part": dk_part,
                "description": (
                    item.get("Description", {}).get("ProductDescription")
                    if item.get("Description")
                    else None
                ),
                "price": item.get("UnitPrice"),
                "image": image_url,
                "url": item.get("ProductUrl"),
                "stock": item.get("QuantityAvailable"),
                "category_path": category_path,
            }
        )

    return products

    return products
