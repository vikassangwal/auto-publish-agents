"""
Abstract Base Class for Platform Connectors.
Defines standard lifecycle hooks for APIs, Browser Automation, and Custom Webhooks.
"""
from abc import ABC, abstractmethod
from typing import Optional
from core.models import ListingPayload, PublishResult, JobStatus, ProductMetadata

class PlatformConnector(ABC):
    def __init__(self, platform_name: str, config: Optional[dict] = None):
        self.platform_name = platform_name
        self.config = config or {}

    @abstractmethod
    def prepare_listing(self, product: ProductMetadata) -> ListingPayload:
        """Adapts the raw product metadata into platform-specific format."""
        pass

    @abstractmethod
    def publish(self, payload: ListingPayload, dry_run: bool = False) -> PublishResult:
        """Publishes the listing or creates a draft."""
        pass

    @abstractmethod
    def verify(self, listing_url: str) -> bool:
        """Verifies if the published listing is live and accessible."""
        pass
