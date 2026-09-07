"""
Custom GPT & AI App Webhook Server.
Allows ChatGPT Custom GPTs or mobile AI apps to trigger end-to-end
product creation, packaging, and 20-platform distribution via a single URL/Action.
"""
import os
import json
from pathlib import Path
from typing import Optional, List, Dict
from fastapi import FastAPI, HTTPException, Request, BackgroundTasks
from pydantic import BaseModel, Field
from core.product_generator import ProductGenerator
from core.ingest import ProductIngestionEngine
from core.publisher import PublisherOrchestrator
from core.reporter import PublishReporter
from core.store_reader import StoreReader

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

class PublishRequest(BaseModel):
    prompt: Optional[str] = Field(None, description="Idea/topic for the digital product to generate (e.g. 'Gym Fitness & Diet Tracker')")
    product_file: Optional[str] = Field(None, description="Existing file name in workspace if publishing an already created file")
    format_type: str = Field("spreadsheet", description="Type of product: 'spreadsheet', 'document', or 'code'")
    no_api: bool = Field(True, description="Whether to use Zero-API browser automation (default True)")
    auto_approve: bool = Field(True, description="Whether to auto-approve pre-publish checklist")

class PlatformStatusItem(BaseModel):
    platform: str
    status: str
    url: Optional[str]
    message: str

class PublishResponse(BaseModel):
    status: str
    product_title: str
    format_category: str
    bundle_zip: str
    total_platforms: int
    platforms: List[PlatformStatusItem]
    markdown_report: str

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
            markdown_report=md_report
        )

    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    import uvicorn
    print("Starting Auto-Publisher Webhook Server on port 8000...")
    uvicorn.run(app, host="0.0.0.0", port=8000)
