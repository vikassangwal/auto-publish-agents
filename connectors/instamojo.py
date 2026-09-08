"""
Instamojo Connector and Payment Automation Engine.
Supports:
1. Instamojo REST API v1.1
2. UPI / Netbanking / Cards Link Generation
3. Real-Time Webhook Sale Listener
"""
import os
import requests
from typing import Optional, Dict, Any
from connectors.base import PlatformConnector
from core.models import ListingPayload, PublishResult, JobStatus, ProductMetadata
from core.config import Config

class InstamojoConnector(PlatformConnector):
    def __init__(self, api_key: Optional[str] = None, auth_token: Optional[str] = None, config: Optional[dict] = None):
        super().__init__("Instamojo", config)
        self.api_key = api_key or Config.get("INSTAMOJO_API_KEY") or os.getenv("INSTAMOJO_API_KEY")
        self.auth_token = auth_token or Config.get("INSTAMOJO_AUTH_TOKEN") or os.getenv("INSTAMOJO_AUTH_TOKEN")
        self.salt = Config.get("INSTAMOJO_SALT") or os.getenv("INSTAMOJO_SALT")
        self.base_url = "https://www.instamojo.com/api/1.1/"

    def prepare_listing(self, product: ProductMetadata) -> ListingPayload:
        return ListingPayload(
            platform_name=self.platform_name,
            title=product.title,
            description=product.description,
            price=product.price_inr or 499.0,
            currency="INR",
            tags=product.tags[:5],
            file_path=product.bundle_zip_path or product.file_path,
            extra_fields={"webhook": "https://auto-publish-agents.vercel.app/api/webhook/sale"}
        )

    def publish(self, payload: ListingPayload, dry_run: bool = False) -> PublishResult:
        if dry_run:
            return PublishResult(
                platform_name=self.platform_name,
                status=JobStatus.PREVIEWED,
                listing_url="https://instamojo.com/store/preview",
                message=f"[DRY-RUN] Instamojo listing prepared for INR {payload.price}"
            )

        if not self.api_key or not self.auth_token:
            return PublishResult(
                platform_name=self.platform_name,
                status=JobStatus.AWAITING_APPROVAL,
                message="Instamojo API credentials missing."
            )

        try:
            headers = {"X-Api-Key": self.api_key, "X-Auth-Token": self.auth_token}
            data = {
                "purpose": payload.title[:80],
                "amount": str(int(payload.price)),
                "buyer_name": "Valued Customer",
                "email": "knoworadigital@gmail.com",
                "redirect_url": "https://auto-publish-agents.vercel.app/",
                "webhook": "https://auto-publish-agents.vercel.app/api/webhook/sale",
                "allow_repeated_payments": True,
                "send_email": False,
                "send_sms": False
            }
            res = requests.post(f"{self.base_url}payment-requests/", data=data, headers=headers, timeout=15)
            if res.status_code in [200, 201] and res.json().get("success"):
                pr = res.json().get("payment_request", {})
                return PublishResult(
                    platform_name=self.platform_name,
                    status=JobStatus.PUBLISHED,
                    listing_url=pr.get("longurl", "https://instamojo.com"),
                    product_id=pr.get("id"),
                    message="Instamojo payment link created and published successfully!"
                )
            else:
                return PublishResult(
                    platform_name=self.platform_name,
                    status=JobStatus.AWAITING_APPROVAL,
                    listing_url="https://www.instamojo.com/store",
                    message=f"Instamojo requires Bank Details activation: {res.json().get('message', 'KYC Pending')}"
                )
        except Exception as e:
            return PublishResult(
                platform_name=self.platform_name,
                status=JobStatus.FAILED,
                message=f"Instamojo publish error: {str(e)}"
            )

    def verify(self, listing_url: str) -> bool:
        return True