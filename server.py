"""
Custom GPT & AI App Webhook Server.
Allows ChatGPT Custom GPTs or mobile AI apps to trigger end-to-end
product creation, packaging, and 20-platform distribution via a single URL/Action.
"""
import os
import json
from pathlib import Path
from typing import Optional, List, Dict, Any
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from pydantic import BaseModel, Field
from core.product_generator import ProductGenerator
from core.ingest import ProductIngestionEngine
from core.publisher import PublisherOrchestrator
from core.reporter import PublishReporter
from core.store_reader import StoreReader
from core.dynamic_store_registry import DynamicStoreRegistry
from core.linkedin_promoter import LinkedInPromoter
from core.session_vault import SessionVault
from core.email_dispatcher import EmailDispatcher

app = FastAPI(
    title="Digital Product Auto-Publisher Agent API",
    description="Autonomous Agent API to create and publish digital products to 20+ marketplaces & websites from Custom GPTs.",
    version="2.0.0",
    docs_url="/docs",
    openapi_url="/openapi.json"
)

@app.middleware("http")
async def vercel_path_normalizer(request: Request, call_next):
    """
    Normalizes URLs when deployed behind Vercel rewrites.
    Maps /api/index.py or rewritten paths back to their true FastAPI routes.
    """
    matched = request.headers.get("x-matched-path")
    if matched:
        request.scope["path"] = matched
    elif request.scope.get("path") in ["/api/index.py", "/api/index", "/api"]:
        request.scope["path"] = "/"
    elif request.scope.get("path", "").startswith("/api/index.py/"):
        request.scope["path"] = request.scope["path"][len("/api/index.py"):]

    return await call_next(request)

class AddStoreRequest(BaseModel):
    name: str = Field(..., description="Display name for the website or store (e.g. 'My WordPress Store')")
    url: str = Field(..., description="Base URL of the website (e.g. 'https://mystore.com')")
    type: str = Field("woocommerce", description="Type of store: 'woocommerce', 'shopify', 'custom_webhook', or 'marketplace'")
    api_key: Optional[str] = Field(None, description="Consumer Key or Shopify Access Token (if API based)")
    api_secret: Optional[str] = Field(None, description="Consumer Secret for WooCommerce (optional)")
    new_product_url: Optional[str] = Field(None, description="Custom 1-click new product listing URL if marketplace (e.g. Etsy, etc.)")

class AddStoreResponse(BaseModel):
    status: str
    message: str
    store: Dict[str, Any]

class SessionSyncRequest(BaseModel):
    platform: str = Field(..., description="Platform name (e.g. 'Gumroad', 'Etsy', 'Shopify')")
    auth_token_or_cookie: str = Field(..., description="Session token or cookie string")
    expires_in_days: int = Field(180, description="Session validity duration in days")
    device_name: str = Field("User Device", description="Name of device performing the sync")

class SessionStatusResponse(BaseModel):
    all_healthy: bool
    total_monitored: int
    active_sessions_count: int
    logged_out_alerts: List[str]
    platforms: List[Dict[str, Any]]
    multi_device_sync_status: str

class PublishRequest(BaseModel):
    prompt: Optional[str] = Field(None, description="Idea/topic for the digital product to generate (e.g. 'Gym Fitness & Diet Tracker')")
    product_file: Optional[str] = Field(None, description="Existing file name in workspace if publishing an already created file")
    format_type: str = Field("spreadsheet", description="Type of product: 'spreadsheet', 'document', or 'code'")
    no_api: bool = Field(True, description="Whether to use Zero-API browser automation (default True)")
    auto_approve: bool = Field(True, description="Whether to auto-approve pre-publish checklist")
    # Dynamic Store Integration
    custom_store_url: Optional[str] = Field(None, description="Direct URL of user's personal WooCommerce or Shopify store")
    custom_store_type: Optional[str] = Field(None, description="Type of store: 'woocommerce' or 'shopify'")
    custom_store_api_key: Optional[str] = Field(None, description="Shopify Access Token or WooCommerce Consumer Key")
    custom_store_api_secret: Optional[str] = Field(None, description="WooCommerce Consumer Secret (if WooCommerce)")

class PlatformStatusItem(BaseModel):
    platform: str
    status: str
    url: Optional[str]
    message: str

class LinkedInPromoItem(BaseModel):
    headline: str
    post_copy: str
    one_click_share_url: str

class PublishResponse(BaseModel):
    status: str
    product_title: str
    format_category: str
    bundle_zip: str
    total_platforms: int
    platforms: List[PlatformStatusItem]
    markdown_report: str
    linkedin_promo: Optional[LinkedInPromoItem] = None

class EmailSendRequest(BaseModel):
    to_email: str = Field(..., description="Recipient email address (e.g. 'client@example.com')")
    subject: str = Field(..., description="Subject line of the email")
    body: Optional[str] = Field(None, description="Body content of the email or instructions for the pitch")
    product_link: Optional[str] = Field(None, description="Optional link to digital product or store")
    email_type: str = Field("promotional", description="Type: 'promotional', 'client_pitch', 'order_delivery', or 'custom'")
    sender_email: Optional[str] = Field(None, description="Optional sender email (e.g. your_email@gmail.com)")
    sender_password: Optional[str] = Field(None, description="Optional sender password or Gmail App Password")

class EmailSendResponse(BaseModel):
    status: str
    sent_via_smtp: bool
    to_email: str
    subject: str
    message: str
    one_click_mailto_url: str
    preview_text: str

@app.get("/")
@app.get("/api")
@app.get("/api/index")
@app.get("/api/index.py")
def health_check():
    return {
        "status": "online",
        "agent": "Digital Product Auto-Publisher Agent",
        "version": "2.0.0",
        "supported_platforms": 20,
        "docs_url": "/docs",
        "openapi_url": "/openapi.json"
    }

@app.get("/api/platforms")
def list_platforms():
    return {
        "marketplaces": [
            "Gumroad", "Lemon Squeezy", "Payhip", "Sellfy", "Whop", "Stan Store",
            "Etsy", "Creative Market", "AppSumo", "CodeCanyon", "Product Hunt",
            "BetaList", "Cosmofeed", "Instamojo", "Razorpay Pages", "TagMango",
            "Graphy", "Podia", "Fiverr", "Upwork"
        ],
        "multi_site_support": "10 to 50 personal websites via websites.json (WooCommerce, Shopify, Webhooks)"
    }

@app.get("/api/analytics")
def get_store_analytics():
    """
    Returns revenue, sales count, and order intelligence across connected stores for Custom GPT.
    """
    reader = StoreReader()
    return reader.get_analytics()

@app.get("/api/products")
def list_store_products():
    """
    Lists all active and draft products across Gumroad, Etsy, WooCommerce, and Shopify.
    """
    reader = StoreReader()
    return {"products": reader.list_all_products()}

@app.get("/api/stores")
def get_store_connections():
    """
    Checks live connection status of all 20 marketplaces and personal websites.
    """
    reader = StoreReader()
    return {"stores": reader.get_store_connections()}

@app.post("/api/stores/add", response_model=AddStoreResponse)
def add_new_store(req: AddStoreRequest):
    """
    Called by Custom GPT to dynamically connect and register ANY new website or marketplace.
    """
    registry = DynamicStoreRegistry()
    saved = registry.register_store(
        name=req.name,
        url=req.url,
        store_type=req.type,
        api_key=req.api_key,
        api_secret=req.api_secret,
        new_product_url=req.new_product_url
    )
    return AddStoreResponse(
        status="SUCCESS",
        message=f"Store '{req.name}' successfully connected and registered for auto-publishing!",
        store=saved
    )

@app.get("/api/session/status", response_model=SessionStatusResponse)
def check_login_sessions():
    """
    Called by Custom GPT to proactively monitor login status across all stores
    and alert if any store has been logged out.
    """
    vault = SessionVault()
    return vault.get_all_session_statuses()

@app.post("/api/session/sync")
def sync_device_session(req: SessionSyncRequest):
    """
    Syncs authenticated session from any device (phone, laptop, PC) into the Cloud Vault.
    """
    vault = SessionVault()
    return vault.sync_session_from_device(
        platform=req.platform,
        auth_token_or_cookie=req.auth_token_or_cookie,
        expires_in_days=req.expires_in_days,
        device_name=req.device_name
    )

@app.post("/api/email/send", response_model=EmailSendResponse)
def send_professional_email(req: EmailSendRequest):
    """
    Called by Custom GPT to compose and send professional emails (pitches, deliveries, promotions).
    """
    res = EmailDispatcher.compose_and_send(
        to_email=req.to_email,
        subject=req.subject,
        body=req.body,
        product_link=req.product_link,
        email_type=req.email_type,
        sender_email=req.sender_email,
        sender_password=req.sender_password
    )
    return EmailSendResponse(**res)

@app.post("/api/publish", response_model=PublishResponse)
def publish_digital_product(req: PublishRequest):
    """
    Called by Custom GPT to build and publish a digital product to all platforms.
    """
    try:
        # 1. Product Resolution or Generation
        if req.prompt:
            gen = ProductGenerator()
            product_path = gen.generate_product(req.prompt, asset_type=req.format_type)
        elif req.product_file:
            product_path = Path(req.product_file)
            if not product_path.is_absolute():
                repo_file = Path(__file__).resolve().parent / req.product_file
                product_path = repo_file if repo_file.exists() else Path(req.product_file)
        else:
            product_path = Path(__file__).resolve().parent / "Ultimate_Investment_Portfolio_Tracker_Pro.xlsx"

        if not product_path.exists():
            raise HTTPException(status_code=404, detail=f"File not found: {product_path}")

        # 2. Ingestion & Analysis
        engine = ProductIngestionEngine(str(product_path))
        product_meta = engine.analyze()

        # 3. Publish to all 20 platforms + personal sites
        orchestrator = PublisherOrchestrator(
            product=product_meta,
            auto_approve=req.auto_approve,
            dry_run=False,
            no_api=req.no_api
        )
        results = orchestrator.run()

        # 3b. On-the-fly Dynamic Store Deployment (if provided directly by user in prompt)
        if req.custom_store_url and req.custom_store_api_key:
            custom_res = orchestrator.multi_site_manager.deploy_custom_store(
                store_url=req.custom_store_url,
                store_type=req.custom_store_type or "woocommerce",
                api_key=req.custom_store_api_key,
                api_secret=req.custom_store_api_secret,
                product=product_meta
            )
            results.insert(0, custom_res)

        # 4. Generate Report
        if os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
            import tempfile
            out_dir = Path(tempfile.gettempdir()) / "output"
        else:
            out_dir = Path(__file__).resolve().parent / "output"
        try:
            out_dir.mkdir(parents=True, exist_ok=True)
        except (OSError, PermissionError):
            import tempfile
            out_dir = Path(tempfile.gettempdir()) / "output"
            out_dir.mkdir(parents=True, exist_ok=True)

        reporter = PublishReporter(product=product_meta, results=results, output_dir=str(out_dir))
        md_report = reporter.generate_report()

        # 5. Generate LinkedIn Viral Promotion with 1-Click Share Link
        primary_link = next(
            (r.listing_url for r in results if r.listing_url and ("gumroad" in r.listing_url.lower() or "etsy" in r.listing_url.lower())),
            results[0].listing_url if results else "https://auto-publish-agents.vercel.app"
        )
        promo_data = LinkedInPromoter.generate_promotion(product_meta, primary_link)
        linkedin_item = LinkedInPromoItem(
            headline=promo_data["headline"],
            post_copy=promo_data["post_copy"],
            one_click_share_url=promo_data["one_click_share_url"]
        )

        platform_items = [
            PlatformStatusItem(
                platform=r.platform_name,
                status=r.status.value,
                url=r.listing_url,
                message=r.message
            )
            for r in results
        ]

        return PublishResponse(
            status="SUCCESS",
            product_title=product_meta.title,
            format_category=product_meta.format_category,
            bundle_zip=product_meta.bundle_zip_path or str(product_path),
            total_platforms=len(results),
            platforms=platform_items,
            markdown_report=md_report,
            linkedin_promo=linkedin_item
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("Starting Auto-Publisher Webhook Server on port 8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
