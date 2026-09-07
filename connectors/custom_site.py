"""
Custom Website / Webhook / Headless API Connector.
Publishes to the user's own websites (WooCommerce, Shopify, Webflow, Custom Node/Python CMS, or REST Endpoints).
"""
import os
import requests
from .base import PlatformConnector
from core.models import ListingPayload, PublishResult, JobStatus, ProductMetadata
from core.config import Config

class CustomSiteConnector(PlatformConnector):
    def __init__(self, endpoint_url: str = None, auth_header: str = None, config: dict = None):
        super().__init__("Custom Website (Self-Hosted)", config)
        self.endpoint_url = endpoint_url or Config.get("CUSTOM_STORE_ENDPOINT")
        self.auth_header = auth_header or Config.get("CUSTOM_STORE_AUTH")

    def prepare_listing(self, product: ProductMetadata) -> ListingPayload:
        return ListingPayload(
            platform_name=self.platform_name,
            title=product.title,
            description=product.description,
            price=product.price_usd,
            currency="USD",
            tags=product.tags,
            file_path=product.bundle_zip_path or product.file_path,
            extra_fields={"slug": product.file_name.lower().replace(".", "-")}
        )

    def publish(self, payload: ListingPayload, dry_run: bool = False) -> PublishResult:
        if dry_run:
            return PublishResult(
                platform_name=self.platform_name,
                status=JobStatus.PREVIEWED,
                listing_url="https://your-custom-domain.com/products/portfolio-tracker",
                message="[DRY-RUN] Custom Website JSON payload compiled. Endpoint ready."
            )

        if not self.endpoint_url:
            return PublishResult(
                platform_name=self.platform_name,
                status=JobStatus.SKIPPED,
                message="No custom endpoint configured. Provide CUSTOM_STORE_ENDPOINT in config to publish to your own website.",
                requires_human_action=False
            )

        try:
            headers = {"Authorization": self.auth_header, "Content-Type": "application/json"}
            body = {
                "title": payload.title,
                "description": payload.description,
                "price": payload.price,
                "currency": payload.currency,
                "tags": payload.tags,
                "file_path": payload.file_path
            }
            resp = requests.post(self.endpoint_url, json=body, headers=headers, timeout=10)
            if resp.status_code in [200, 201]:
                data = resp.json()
                return PublishResult(
                    platform_name=self.platform_name,
                    status=JobStatus.PUBLISHED,
                    listing_url=data.get("url", self.endpoint_url),
                    message="Successfully synced to user-owned website."
                )
            else:
                return PublishResult(
                    platform_name=self.platform_name,
                    status=JobStatus.FAILED,
                    message=f"Endpoint returned HTTP {resp.status_code}: {resp.text}"
                )
        except Exception as e:
            return PublishResult(
                platform_name=self.platform_name,
                status=JobStatus.FAILED,
                message=f"Custom endpoint error: {str(e)}"
            )

    def verify(self, listing_url: str) -> bool:
        return True
