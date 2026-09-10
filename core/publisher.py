"""
Publisher Orchestrator Engine.
Coordinates parallel/sequential connector execution, handles retries,
and collates publishing reports.
"""
import time
from typing import List, Dict
from .models import ProductMetadata, PublishResult, JobStatus
from .approval_gate import ApprovalGate
from connectors.base import PlatformConnector
from connectors.gumroad import GumroadConnector
from connectors.lemon_squeezy import LemonSqueezyConnector
from connectors.custom_site import CustomSiteConnector
from connectors.generic_marketplace import MarketplaceConnector
from connectors.browser_runner import ZeroApiBrowserRunner
from connectors.multi_site_manager import MultiSiteManager

class PublisherOrchestrator:
    def __init__(self, product: ProductMetadata, auto_approve: bool = False, dry_run: bool = False, no_api: bool = False):
        self.product = product
        self.auto_approve = auto_approve
        self.dry_run = dry_run
        self.no_api = no_api
        self.browser_runner = ZeroApiBrowserRunner() if no_api else None
        self.multi_site_manager = MultiSiteManager()
        self.gate = ApprovalGate(auto_approve=auto_approve)
        
        # Self-Healing Asset Resolver: Ensures file and image always exist!
        from core.auto_asset_builder import AutoAssetBuilder
        builder = AutoAssetBuilder()
        prod_cat = getattr(self.product, "product_type", "Finance")
        current_path = getattr(self.product, "file_path", None)
        valid_file = builder.ensure_deliverable_file(
            title=self.product.title,
            category=prod_cat,
            existing_path=current_path
        )
        self.product.file_path = valid_file
        self.product.bundle_zip_path = valid_file
        setattr(self.product, "thumbnail_url", builder.ensure_main_image(
            title=self.product.title,
            category=prod_cat,
            existing_url=getattr(self.product, "thumbnail_url", None)
        ))
        
        self.connectors: List[PlatformConnector] = []
        self._initialize_connectors()

    def _initialize_connectors(self):
        # 1. High Priority Direct Creator Storefronts
        self.connectors.append(GumroadConnector())
        self.connectors.append(LemonSqueezyConnector())
        self.connectors.append(MarketplaceConnector("Payhip", mode="api_or_browser"))
        self.connectors.append(MarketplaceConnector("Sellfy", mode="api_or_browser"))
        self.connectors.append(MarketplaceConnector("Whop", mode="api_or_browser"))
        self.connectors.append(MarketplaceConnector("Stan Store", mode="browser_or_review"))
        
        # 2. Organic Marketplaces & Design Hubs
        self.connectors.append(MarketplaceConnector("Etsy", mode="browser_or_review"))
        self.connectors.append(MarketplaceConnector("Creative Market", mode="browser_or_review"))
        self.connectors.append(MarketplaceConnector("AppSumo", mode="browser_or_review"))
        self.connectors.append(MarketplaceConnector("CodeCanyon", mode="review"))

        # 3. Launch & Tech Promotion Platforms
        self.connectors.append(MarketplaceConnector("Product Hunt", mode="launch_workflow"))
        self.connectors.append(MarketplaceConnector("BetaList", mode="submission"))

        # 4. India & Regional Multi-Currency Storefronts
        self.connectors.append(MarketplaceConnector("Cosmofeed", mode="browser_or_review"))
        self.connectors.append(MarketplaceConnector("Instamojo", mode="browser_or_review"))
        self.connectors.append(MarketplaceConnector("Razorpay Pages", mode="review"))
        self.connectors.append(MarketplaceConnector("TagMango", mode="browser_or_review"))
        self.connectors.append(MarketplaceConnector("Graphy", mode="browser_or_review"))

        # 5. Creator Hubs & Freelance Catalogs
        self.connectors.append(MarketplaceConnector("Podia", mode="browser_or_review"))
        self.connectors.append(MarketplaceConnector("Fiverr", mode="review"))
        self.connectors.append(MarketplaceConnector("Upwork", mode="review"))

    def run(self) -> List[PublishResult]:
        # 1. Prepare all platform payloads
        payloads = [c.prepare_listing(self.product) for c in self.connectors]

        # 2. Render preview and request human gate approval
        self.gate.render_preview(self.product, payloads)
        approved = self.gate.request_approval()

        if not approved:
            print("\n[CANCELLED] Operation aborted by user.")
            return [PublishResult(platform_name=c.platform_name, status=JobStatus.SKIPPED, message="User cancelled pre-publish approval") for c in self.connectors]

        # 3. Execute publishing pipeline
        results: List[PublishResult] = []
        print("\nExecuting distribution pipeline across target platforms...")

        for connector, payload in zip(self.connectors, payloads):
            print(f" -> Deploying to {connector.platform_name}...", end=" ", flush=True)
            if self.no_api and not self.dry_run:
                res = self.browser_runner.publish_via_browser(connector.platform_name, payload)
            else:
                res = connector.publish(payload, dry_run=self.dry_run)
            self.gate.handle_challenge(res)
            print(f"[{res.status.value.upper()}]")
            results.append(res)
            time.sleep(0.05) # Prevent aggressive rate bursts

        # 4. Execute Multi-Site Deployment across personal websites
        site_results = self.multi_site_manager.publish_to_all_sites(self.product, dry_run=self.dry_run)
        results.extend(site_results)

        return results
