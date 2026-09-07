"""
Core data models for the Digital Product Auto-Publisher Agent.
"""
from dataclasses import dataclass, field
from enum import Enum
from typing import List, Dict, Optional, Any
from datetime import datetime

class PublishMode(str, Enum):
    API = "api"
    BROWSER = "browser"
    API_OR_BROWSER = "api_or_browser"
    REVIEW_REQUIRED = "review_required"
    WEBHOOK = "webhook"

class JobStatus(str, Enum):
    PENDING = "pending"
    PREVIEWED = "previewed"
    AWAITING_APPROVAL = "awaiting_approval"
    AWAITING_OTP = "awaiting_otp"
    IN_PROGRESS = "in_progress"
    PUBLISHED = "published"
    DRAFT_SAVED = "draft_saved"
    FAILED = "failed"
    SKIPPED = "skipped"

@dataclass
class ProductMetadata:
    file_path: str
    file_name: str
    product_type: str
    format_category: str = "General Digital"
    title: str = ""
    tagline: str = ""
    description: str = ""
    key_features: List[str] = field(default_factory=list)
    price_usd: float = 29.0
    price_inr: float = 1999.0
    currency: str = "USD"
    tags: List[str] = field(default_factory=list)
    suggested_categories: List[str] = field(default_factory=list)
    recommended_channels: List[str] = field(default_factory=list)
    bundle_zip_path: Optional[str] = None
    demo_file_path: Optional[str] = None

@dataclass
class ListingPayload:
    platform_name: str
    title: str
    description: str
    price: float
    currency: str
    tags: List[str]
    file_path: str
    extra_fields: Dict[str, Any] = field(default_factory=dict)

@dataclass
class PublishResult:
    platform_name: str
    status: JobStatus
    listing_url: Optional[str] = None
    product_id: Optional[str] = None
    message: str = ""
    requires_human_action: bool = False
    action_type: Optional[str] = None  # OTP, CAPTCHA, Identity, Bank Setup
    timestamp: str = field(default_factory=lambda: datetime.now().isoformat())
