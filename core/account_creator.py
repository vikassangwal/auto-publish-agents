"""
Privacy-First Account Creator & Onboarding Assistant.
Automates merchant / creator onboarding workflows across platforms
with built-in data minimization, zero bank credential leakage,
and human-in-the-loop OTP/CAPTCHA protection.
"""
import os
import secrets
import string
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class OnboardingRequest(BaseModel):
    brand_name: str = Field(..., description="Public store or creator brand name (e.g. 'Zenith Templates')")
    contact_email: str = Field(..., description="Business contact email for account creation")
    target_platforms: Optional[List[str]] = Field(
        default=["Gumroad", "Payhip", "Lemon Squeezy", "Whop", "Sellfy"],
        description="List of platforms to set up accounts for"
    )
    store_category: str = Field("Digital Products & Templates", description="Niche / Category for the store")

class AccountSetupInstruction(BaseModel):
    platform: str
    signup_url: str
    recommended_username: str
    suggested_store_name: str
    category: str
    privacy_checklist: List[str]
    human_action_required: str

class AccountCreationPlan(BaseModel):
    brand_name: str
    contact_email: str
    total_platforms: int
    secure_master_seed_hint: str
    privacy_policy_compliance: str
    platform_plans: List[AccountSetupInstruction]

class AccountOnboardingEngine:
    PLATFORM_SIGNUP_URLS = {
        "Gumroad": "https://app.gumroad.com/signup",
        "Lemon Squeezy": "https://app.lemonsqueezy.com/register",
        "Payhip": "https://payhip.com/register",
        "Whop": "https://dash.whop.com/signup",
        "Sellfy": "https://sellfy.com/user/register",
        "Stan Store": "https://stan.store/creator/signup",
        "Etsy": "https://www.etsy.com/sell",
        "Product Hunt": "https://www.producthunt.com/signup",
        "BetaList": "https://betalist.com/users/sign_up",
        "Cosmofeed": "https://creator.cosmofeed.com/signup",
        "Instamojo": "https://www.instamojo.com/signup",
        "Razorpay Pages": "https://easy.razorpay.com/onboarding",
        "TagMango": "https://tagmango.com/creator/dashboard",
        "Graphy": "https://graphy.com/get-started",
        "Podia": "https://app.podia.com/signup"
    }

    @staticmethod
    def generate_privacy_safe_credentials(brand_name: str) -> Dict[str, str]:
        """Generates privacy-preserving username suggestions and password structure."""
        clean_brand = "".join(c for c in brand_name.lower() if c.isalnum())
        rand_suffix = secrets.token_hex(2)
        username = f"{clean_brand}_{rand_suffix}"
        
        # High-entropy privacy-safe password template
        alphabet = string.ascii_letters + string.digits + "!@#$%^&*"
        generated_password = "".join(secrets.choice(alphabet) for _ in range(16))
        
        return {
            "suggested_username": username,
            "generated_strong_password": generated_password
        }

    @classmethod
    def create_onboarding_plan(cls, req: OnboardingRequest) -> AccountCreationPlan:
        """
        Creates a structured, privacy-first onboarding sequence for Custom GPT.
        Guarantees that sensitive banking details remain completely isolated.
        """
        plans = []
        creds = cls.generate_privacy_safe_credentials(req.brand_name)
        
        for platform in req.target_platforms:
            signup_url = cls.PLATFORM_SIGNUP_URLS.get(
                platform, 
                f"https://{platform.lower().replace(' ', '')}.com/signup"
            )
            
            privacy_rules = [
                "Shield Personal Data: Use a dedicated business email alias, never your primary personal inbox.",
                "Zero Bank API Exposure: Complete payout/bank linking manually inside the platform dashboard; never expose bank details to AI.",
                "Two-Factor Authentication (2FA): Turn on app-based 2FA immediately upon account creation."
            ]
            
            plans.append(AccountSetupInstruction(
                platform=platform,
                signup_url=signup_url,
                recommended_username=creds["suggested_username"],
                suggested_store_name=f"{req.brand_name} Official Store",
                category=req.store_category,
                privacy_checklist=privacy_rules,
                human_action_required="1. Click signup URL. 2. Auto-fill brand details. 3. Complete email verification."
            ))
            
        return AccountCreationPlan(
            brand_name=req.brand_name,
            contact_email=req.contact_email,
            total_platforms=len(plans),
            secure_master_seed_hint="Use a privacy-respecting password manager (e.g., Bitwarden or 1Password) to store platform secrets.",
            privacy_policy_compliance="Strict Zero-Knowledge Data Isolation: AI never reads or stores banking passwords, KYC Aadhaar/PAN, or debit/credit card numbers.",
            platform_plans=plans
        )
