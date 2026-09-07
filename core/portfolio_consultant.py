"""
Interactive Creator Portfolio & Consultative Selling Engine.
1. Showcases the user's live digital products with features, prices, and demo links.
2. Explains all categories of digital products the user can build (Custom Spreadsheets, SaaS Boilerplates, Notion Dashboards, Automation Bots, etc.).
3. Acts as an active consultative sales listener: asks discovery questions, listens to customer needs, and gives smart, tailored recommendations.
"""
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class CustomerConsultationRequest(BaseModel):
    customer_query: str = Field(..., description="What the customer is saying, asking, or looking for")
    customer_budget: Optional[str] = Field(None, description="Customer's budget range if mentioned")
    industry_or_niche: Optional[str] = Field(None, description="Customer's industry (e.g., Real Estate, Crypto, Fitness, Agency, E-commerce)")

class ProductShowcaseItem(BaseModel):
    title: str
    category: str
    price_usd: float
    price_inr: float
    key_features: List[str]
    best_for: str
    live_url: str

class SkillCapability(BaseModel):
    domain: str
    what_i_can_build: List[str]
    turnaround_time: str
    customization_level: str

class ConsultationResponse(BaseModel):
    active_listening_summary: str
    recommended_projects: List[ProductShowcaseItem]
    custom_build_options: List[SkillCapability]
    smart_suggestion_for_customer: str
    interactive_followup_question: str
    chat_presentation_card: str

class PortfolioConsultationEngine:
    # 1. Catalog of existing ready-to-sell projects
    SHOWCASE_PROJECTS = [
        ProductShowcaseItem(
            title="Ultimate Investment Portfolio Tracker Pro",
            category="Finance & Wealth Intelligence",
            price_usd=29.0,
            price_inr=1999.0,
            key_features=[
                "Multi-Asset Coverage: Stocks, Crypto, Mutual Funds, Gold, Real Estate",
                "Automated Portfolio Rebalancing with Tax-Drift Alerts",
                "FIRE Freedom & Retirement Cashflow Simulator",
                "Macro-Free & 100% Google Sheets + Excel Compatible"
            ],
            best_for="Investors, high-net-worth individuals, solopreneurs",
            live_url="https://auto-publish-agents.vercel.app/products"
        ),
        ProductShowcaseItem(
            title="SaaS & Startup Financial Runway Model",
            category="Business & Financial Modeling",
            price_usd=39.0,
            price_inr=2999.0,
            key_features=[
                "CAC, LTV, MRR, Churn & Burn Rate Automated Forecasting",
                "Investor-Ready Pitch Deck Valuation Tables (DCF & Multiple)",
                "Scenario Planning (Worst-case, Expected, Bull-case)"
            ],
            best_for="Startup founders, agency owners, business consultants",
            live_url="https://auto-publish-agents.vercel.app/products"
        ),
        ProductShowcaseItem(
            title="Real Estate Rental ROI & Cash Flow Analyzer",
            category="Property & Real Estate",
            price_usd=24.0,
            price_inr=1799.0,
            key_features=[
                "Cap Rate, Cash-on-Cash Return & Net Operating Income (NOI)",
                "30-Year Mortgage Amortization with Extra Payment Impact",
                "Renovation Cost Estimator & Fix-and-Flip Calculator"
            ],
            best_for="Real estate investors, Airbnb hosts, property managers",
            live_url="https://auto-publish-agents.vercel.app/products"
        ),
        ProductShowcaseItem(
            title="Solopreneur & Agency All-in-One Operations Hub",
            category="Productivity & Operations",
            price_usd=34.0,
            price_inr=2499.0,
            key_features=[
                "Client CRM, Pipeline Tracker, and Project Milestone Gantt",
                "Automated Invoicing & Profit/Loss Balance Sheet",
                "Social Media Content Calendar & Campaign Tracker"
            ],
            best_for="Freelancers, agency founders, digital creators",
            live_url="https://auto-publish-agents.vercel.app/products"
        )
    ]

    # 2. What the creator can build on-demand (Custom offerings)
    CAPABILITIES = [
        SkillCapability(
            domain="Advanced Automated Spreadsheets & Dashboards",
            what_i_can_build=[
                "Custom Dynamic Financial Models with automated formulas",
                "Executive KPI Dashboards with interactive visual charts",
                "Google Sheets & Excel multi-currency business trackers"
            ],
            turnaround_time="24 - 48 Hours",
            customization_level="100% Bespoke to your exact requirements"
        ),
        SkillCapability(
            domain="SaaS Boilerplates & Python Automation Bots",
            what_i_can_build=[
                "Multi-platform publisher bots & webhook integrations",
                "Data scraping, workflow automation, and email dispatcher tools",
                "FastAPI & REST APIs deployed to Vercel/Cloud"
            ],
            turnaround_time="2 - 4 Days",
            customization_level="Full source code + commercial license"
        ),
        SkillCapability(
            domain="Digital Planners, SOPs & Business Playbooks",
            what_i_can_build=[
                "Notion Workspace Architecture & Team Workspaces",
                "Printable Planners, Workbooks, and Checklists (.pdf/.docx)",
                "Company Standard Operating Procedures (SOPs)"
            ],
            turnaround_time="24 Hours",
            customization_level="White-label with your brand identity"
        )
    ]

    @classmethod
    def consult_customer(cls, req: CustomerConsultationRequest) -> ConsultationResponse:
        query_lower = req.customer_query.lower()

        # Match relevant projects
        matched_projects = []
        for proj in cls.SHOWCASE_PROJECTS:
            if any(k in query_lower for k in ["invest", "crypto", "stock", "wealth", "portfolio"]) and "investment" in proj.title.lower():
                matched_projects.append(proj)
            elif any(k in query_lower for k in ["startup", "saas", "runway", "business", "valuation"]) and "saas" in proj.title.lower():
                matched_projects.append(proj)
            elif any(k in query_lower for k in ["property", "real estate", "rental", "house", "roi"]) and "real estate" in proj.title.lower():
                matched_projects.append(proj)
            elif any(k in query_lower for k in ["agency", "client", "freelance", "crm", "project"]) and "agency" in proj.title.lower():
                matched_projects.append(proj)

        # Fallback to top 2 popular templates if no specific match
        if not matched_projects:
            matched_projects = cls.SHOWCASE_PROJECTS[:2]

        # Active listening reflection
        listening_summary = (
            f"I hear you! You are looking for a high-performance system to streamline your {req.industry_or_niche or 'workflows'}. "
            f"Based on what you mentioned ('{req.customer_query[:100]}...'), here is what we have ready right now, and what we can custom-build for you."
        )

        # Consultative smart suggestion
        smart_suggestion = (
            f"💡 **My Recommendation:** If you need immediate results today, our '{matched_projects[0].title}' gives you a complete, ready-to-run system. "
            f"However, if you have proprietary calculations, custom workflows, or specific branding, I can build a 100% custom-tailored system for you within 24-48 hours."
        )

        # Interactive discovery question (listens to the customer)
        followup_q = (
            "🤝 **Quick question to help you best:** Are you looking for a ready-made template you can use instantly today, "
            "or do you have specific custom features you'd like me to build exclusively for your workflow?"
        )

        # Formatted presentation card for chat
        projects_txt = ""
        for p in matched_projects:
            features_list = "\n".join([f"    • {f}" for f in p.key_features[:3]])
            projects_txt += (
                f"\n📦 **{p.title}** (${p.price_usd:.2f} / ₹{p.price_inr:.0f})\n"
                f"  *Category:* {p.category}\n"
                f"  *Features:*\n{features_list}\n"
                f"  *Best For:* {p.best_for}\n"
                f"  👉 [Explore Project Details]({p.live_url})\n"
            )

        presentation_card = (
            f"### 🌟 Here Is What I Can Do For You:\n\n"
            f"{listening_summary}\n\n"
            f"#### 1. Ready-Made Projects You Can Access Instantly:\n{projects_txt}\n"
            f"#### 2. What Else I Can Custom-Build For You:\n"
            f"• **Automated Spreadsheets & Models:** Financial models, ROI tools, KPI dashboards.\n"
            f"• **Automation Bots & APIs:** Python bots, automated publishers, custom webhooks.\n"
            f"• **Digital Systems & SOPs:** Notion hubs, client portals, business systems.\n\n"
            f"{smart_suggestion}\n\n"
            f"{followup_q}"
        )

        return ConsultationResponse(
            active_listening_summary=listening_summary,
            recommended_projects=matched_projects,
            custom_build_options=cls.CAPABILITIES,
            smart_suggestion_for_customer=smart_suggestion,
            interactive_followup_question=followup_q,
            chat_presentation_card=presentation_card
        )
