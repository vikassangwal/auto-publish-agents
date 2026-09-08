"""
Shopify Connector (Admin REST API with Client Credentials token refresh).
Automates product creation, dropshipping inventory listing, and order monitoring.
"""
import os
import requests
from typing import Optional, Dict, Any, List
from .base import PlatformConnector
from core.models import ListingPayload, PublishResult, JobStatus, ProductMetadata
from core.config import Config

class ShopifyConnector(PlatformConnector):
    def __init__(self, shop_domain: str = None, access_token: str = None, client_id: str = None, client_secret: str = None):
        super().__init__("Shopify", {})
        self.shop_domain = shop_domain or os.getenv("SHOPIFY_SHOP_DOMAIN", "digitalknowora.myshopify.com")
        self.access_token = access_token or os.getenv("SHOPIFY_ACCESS_TOKEN", "")
        self.client_id = client_id or os.getenv("SHOPIFY_CLIENT_ID", "")
        self.client_secret = client_secret or os.getenv("SHOPIFY_CLIENT_SECRET", "")
        self.api_version = "2024-01"

    def refresh_access_token(self) -> Optional[str]:
        if not self.client_id or not self.client_secret:
            return None
        token_url = f"https://{self.shop_domain}/admin/oauth/access_token"
        payload = {
            "client_id": self.client_id,
            "client_secret": self.client_secret,
            "grant_type": "client_credentials"
        }
        try:
            res = requests.post(token_url, json=payload, timeout=15)
            if res.status_code == 200:
                data = res.json()
                self.access_token = data.get("access_token")
                return self.access_token
        except Exception as e:
            print(f"[Shopify] Token refresh error: {e}")
        return None

    def _get_headers(self) -> dict:
        return {
            "X-Shopify-Access-Token": self.access_token,
            "Content-Type": "application/json"
        }

    def get_shop_info(self) -> Dict[str, Any]:
        url = f"https://{self.shop_domain}/admin/api/{self.api_version}/shop.json"
        res = requests.get(url, headers=self._get_headers(), timeout=15)
        if res.status_code == 401:
            self.refresh_access_token()
            res = requests.get(url, headers=self._get_headers(), timeout=15)
        return res.json() if res.status_code == 200 else {"error": res.text, "status_code": res.status_code}

    def create_product(
        self,
        title: str,
        body_html: str,
        price: float,
        compare_at_price: Optional[float] = None,
        tags: Optional[List[str]] = None,
        images: Optional[List[Dict[str, str]]] = None,
        product_type: str = "Dropshipping",
        vendor: str = "Digital KnowOra",
        status: str = "active"
    ) -> Dict[str, Any]:
        url = f"https://{self.shop_domain}/admin/api/{self.api_version}/products.json"
        variant_data = {
            "price": str(price),
            "requires_shipping": True
        }
        if compare_at_price:
            variant_data["compare_at_price"] = str(compare_at_price)

        product_payload = {
            "product": {
                "title": title,
                "body_html": body_html,
                "vendor": vendor,
                "product_type": product_type,
                "tags": ", ".join(tags) if tags else "",
                "status": status,
                "variants": [variant_data]
            }
        }
        if images:
            product_payload["product"]["images"] = images

        res = requests.post(url, headers=self._get_headers(), json=product_payload, timeout=20)
        if res.status_code == 401:
            self.refresh_access_token()
            res = requests.post(url, headers=self._get_headers(), json=product_payload, timeout=20)

        if res.status_code in [200, 201]:
            return {"success": True, "product": res.json().get("product")}
        else:
            return {"success": False, "error": res.text, "status_code": res.status_code}

    def list_products(self, limit: int = 10) -> Dict[str, Any]:
        url = f"https://{self.shop_domain}/admin/api/{self.api_version}/products.json?limit={limit}"
        res = requests.get(url, headers=self._get_headers(), timeout=15)
        if res.status_code == 401:
            self.refresh_access_token()
            res = requests.get(url, headers=self._get_headers(), timeout=15)
        return res.json() if res.status_code == 200 else {"error": res.text, "status_code": res.status_code}

    def prepare_listing(self, product: ProductMetadata) -> ListingPayload:
        desc = f"<h3>{product.tagline}</h3><p>{product.description}</p><ul>"
        for feat in product.key_features:
            desc += f"<li>{feat}</li>"
        desc += "</ul>"

        price_inr = product.price_inr or (product.price_usd * 85.0 if product.price_usd else 799.0)

        return ListingPayload(
            platform_name=self.platform_name,
            title=product.title,
            description=desc,
            price=price_inr,
            currency="INR",
            tags=product.tags[:5],
            file_path=product.file_path,
            extra_fields={"compare_at_price": round(price_inr * 1.6, 2)}
        )

    def publish(self, payload: ListingPayload, dry_run: bool = False) -> PublishResult:
        if dry_run:
            slug = payload.title.lower().replace(' ', '-')
            return PublishResult(
                platform_name=self.platform_name,
                status=JobStatus.PREVIEWED,
                listing_url=f"https://{self.shop_domain}/products/{slug}",
                message="[DRY-RUN] Product verified for automated Shopify publication."
            )

        res = self.create_product(
            title=payload.title,
            body_html=payload.description,
            price=payload.price,
            compare_at_price=payload.extra_fields.get("compare_at_price"),
            tags=payload.tags,
            status="active"
        )

        if res.get("success"):
            prod = res["product"]
            handle = prod.get("handle", "")
            return PublishResult(
                platform_name=self.platform_name,
                status=JobStatus.PUBLISHED,
                listing_url=f"https://{self.shop_domain}/products/{handle}",
                product_id=str(prod.get("id")),
                message="Product successfully published to Shopify store!"
            )
        else:
            return PublishResult(
                platform_name=self.platform_name,
                status=JobStatus.FAILED,
                message=f"Shopify publish error: {res.get('error')}"
            )

    def verify(self, listing_url: str) -> bool:
        try:
            r = requests.get(listing_url, timeout=10)
            return r.status_code in [200, 302]
        except Exception:
            return False
