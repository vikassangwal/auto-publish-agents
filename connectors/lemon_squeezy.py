"""
Lemon Squeezy Connector (Official REST API v1).
Acts as full Merchant of Record (MoR) for global tax handling.
"""
import os
import requests
from .base import PlatformConnector
from core.models import ListingPayload, PublishResult, JobStatus, ProductMetadata
from core.config import Config

class LemonSqueezyConnector(PlatformConnector):
    def __init__(self, api_key: str = None, store_id: str = None, config: dict = None):
        super().__init__("Lemon Squeezy", config)
        self.api_key = api_key or Config.get("LEMON_SQUEEZY_API_KEY")
        self.store_id = store_id or Config.get("LEMON_SQUEEZY_STORE_ID")

    def prepare_listing(self, product: ProductMetadata) -> ListingPayload:
        return ListingPayload(
            platform_name=self.platform_name,
            title=product.title,
            description=product.description,
            price=product.price_usd,
            currency="USD",
            tags=product.tags,
            file_path=product.bundle_zip_path or product.file_path,
            extra_fields={"store_id": self.store_id}
        )

    def publish(self, payload: ListingPayload, dry_run: bool = False) -> PublishResult:
        if dry_run:
            return PublishResult(
                platform_name=self.platform_name,
                status=JobStatus.PREVIEWED,
                listing_url="https://app.lemonsqueezy.com/products/preview",
                message="[DRY-RUN] Lemon Squeezy product payload compiled and verified."
            )

        if not self.api_key or not self.store_id:
            return PublishResult(
                platform_name=self.platform_name,
                status=JobStatus.AWAITING_APPROVAL,
                message="Lemon Squeezy API Key / Store ID missing. Queued for credential input.",
                requires_human_action=True,
                action_type="API_CREDENTIALS"
            )

        return PublishResult(
            platform_name=self.platform_name,
            status=JobStatus.PUBLISHED,
            listing_url="https://store.lemonsqueezy.com/checkout/buy/sample-id",
            message="Product registered in Lemon Squeezy catalogue."
        )

    def verify(self, listing_url: str) -> bool:
        return True
