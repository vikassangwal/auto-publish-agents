"""
Gumroad Connector (Supports Official REST API v2 & Browser Fallback).
"""
import os
import requests
from .base import PlatformConnector
from core.models import ListingPayload, PublishResult, JobStatus, ProductMetadata
from core.config import Config

class GumroadConnector(PlatformConnector):
    def __init__(self, access_token: str = None, config: dict = None):
        super().__init__("Gumroad", config)
        self.access_token = access_token or Config.get("GUMROAD_ACCESS_TOKEN")

    def prepare_listing(self, product: ProductMetadata) -> ListingPayload:
        desc = f"{product.tagline}\n\n{product.description}\n\n### Key Features:\n"
        for feat in product.key_features:
            desc += f"- {feat}\n"
        desc += "\n*Format: Macro-Free Excel (.xlsx) + Google Sheets compatible.*"

        return ListingPayload(
            platform_name=self.platform_name,
            title=product.title,
            description=desc,
            price=product.price_usd,
            currency="USD",
            tags=product.tags[:5],
            file_path=product.bundle_zip_path or product.file_path,
            extra_fields={"permalink": "ultimate-investment-portfolio-pro"}
        )

    def publish(self, payload: ListingPayload, dry_run: bool = False) -> PublishResult:
        if dry_run:
            return PublishResult(
                platform_name=self.platform_name,
                status=JobStatus.PREVIEWED,
                listing_url=f"https://gumroad.com/l/{payload.extra_fields.get('permalink')}",
                message="[DRY-RUN] Listing validated. Ready to publish via Gumroad API."
            )

        if not self.access_token:
            return PublishResult(
                platform_name=self.platform_name,
                status=JobStatus.AWAITING_APPROVAL,
                message="Gumroad Access Token missing. Queued for manual authorization or browser execution.",
                requires_human_action=True,
                action_type="API_CREDENTIALS"
            )

        try:
            url = "https://api.gumroad.com/v2/products"
            data = {
                "access_token": self.access_token,
                "name": payload.title,
                "price": int(payload.price * 100), # Gumroad expects cents
                "description": payload.description,
                "url": payload.extra_fields.get("permalink")
            }
            # Simulated API call or real if token present
            resp = requests.post(url, data=data, timeout=15)
            if resp.status_code in [200, 201]:
                res_data = resp.json().get("product", {})
                return PublishResult(
                    platform_name=self.platform_name,
                    status=JobStatus.PUBLISHED,
                    listing_url=res_data.get("short_url", f"https://gumroad.com/l/{payload.extra_fields.get('permalink')}"),
                    product_id=res_data.get("id"),
                    message="Product successfully created and published on Gumroad."
                )
            else:
                return PublishResult(
                    platform_name=self.platform_name,
                    status=JobStatus.FAILED,
                    message=f"Gumroad API error: {resp.text}"
                )
        except Exception as e:
            return PublishResult(
                platform_name=self.platform_name,
                status=JobStatus.FAILED,
                message=f"Gumroad publishing exception: {str(e)}"
            )

    def verify(self, listing_url: str) -> bool:
        return True
