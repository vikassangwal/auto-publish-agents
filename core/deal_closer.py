"""
Autonomous Customer Inbound AI Engine:
1. Summarizes incoming customer / lead inquiries.
2. Identifies customer sentiment, budget, intent, and deal potential.
3. Automatically writes persuasive, deal-closing email replies (with discount / bonus / CTA).
4. Provides instant executive alerts and summary cards for the user in chat.
"""
import re
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field

class CustomerEmailInquiry(BaseModel):
    customer_email: str = Field(..., description="Customer's email address")
    customer_name: Optional[str] = Field("Valued Customer", description="Customer's name")
    subject: str = Field(..., description="Subject of the incoming email")
    email_body: str = Field(..., description="Full text/content of the customer email")
    product_interest: Optional[str] = Field("Digital Templates Suite", description="Product or category the customer asked about")
    target_price: Optional[float] = Field(29.0, description="Standard price of the requested product")
    allow_auto_reply: bool = Field(True, description="Whether to generate and dispatch the deal-closing reply")
    offered_discount_percent: int = Field(15, description="Discount percentage offered to close the deal instantly")

class DealAnalysisResult(BaseModel):
    summary: str
    customer_intent: str
    deal_priority: str
    estimated_deal_value: str
    key_pain_points: List[str]
    suggested_strategy: str
    closing_reply_subject: str
    closing_reply_body: str
    instant_chat_alert: str
    one_click_send_url: str

class DealCloserEngine:
    @staticmethod
    def analyze_and_close_deal(inquiry: CustomerEmailInquiry) -> DealAnalysisResult:
        """
        Analyzes the inbound email, extracts key questions and budget signals,
        formulates an irresistible counter-offer / deal pitch, and outputs a formatted chat notification.
        """
        body_lower = inquiry.email_body.lower()
        
        # 1. Intent & Priority Detection
        intent = "General Inquiry"
        priority = "Medium"
        if any(w in body_lower for w in ["price", "discount", "offer", "deal", "cheap", "cost", "how much"]):
            intent = "Pricing Negotiation / Ready to Buy"
            priority = "HIGH 🔥"
        elif any(w in body_lower for w in ["custom", "feature", "help", "support", "work with", "format", "google sheet"]):
            intent = "Feature Suitability / Commercial Inquiry"
            priority = "HIGH 🔥"
        elif any(w in body_lower for w in ["urgent", "today", "now", "immediately", "team", "business"]):
            intent = "High-Value Enterprise / Immediate Purchaser"
            priority = "CRITICAL ⚡"

        # 2. Extract Pain Points
        pain_points = []
        if "custom" in body_lower or "modify" in body_lower:
            pain_points.append("Needs custom flexibility or formula adaptations.")
        if "team" in body_lower or "license" in body_lower:
            pain_points.append("Interested in multi-user or commercial usage rights.")
        if "discount" in body_lower or "budget" in body_lower:
            pain_points.append("Price-sensitive; looking for an exclusive incentive.")
        if not pain_points:
            pain_points.append("Evaluating solution efficiency and ease-of-use.")

        # 3. Calculate discounted price to close deal
        discounted_price = round(inquiry.target_price * (1 - (inquiry.offered_discount_percent / 100)), 2)

        # 4. Generate Deal-Closing Reply Copy
        reply_subject = f"Re: {inquiry.subject} — Exclusive {inquiry.offered_discount_percent}% VIP Access for you"
        reply_body = (
            f"Hi {inquiry.customer_name},\n\n"
            f"Thank you for reaching out regarding the {inquiry.product_interest}!\n\n"
            f"To answer your inquiry: our system is 100% macro-free, fully customizable, and designed to save you hours of manual work every week.\n\n"
            f"Because you reached out directly, I'd love to extend an exclusive {inquiry.offered_discount_percent}% VIP Welcome Discount to get you started immediately:\n\n"
            f"👉 Special Deal Price: ${discounted_price:.2f} (Regular ${inquiry.target_price:.2f})\n"
            f"👉 Includes: Complete source template + Step-by-Step Video Guide + Lifetime Updates + Commercial License.\n\n"
            f"You can secure this deal right here:\n"
            f"https://auto-publish-agents.vercel.app/products\n\n"
            f"If you have any specific requirements or questions, just reply to this email—I'm here to help you get the maximum value.\n\n"
            f"Best regards,\n"
            f"Vikas & The Digital Products Team"
        )

        import urllib.parse
        enc_subj = urllib.parse.quote(reply_subject)
        enc_body = urllib.parse.quote(reply_body)
        one_click_url = f"mailto:{inquiry.customer_email}?subject={enc_subj}&body={enc_body}"

        # 5. Executive Chat Alert for the User
        chat_alert = (
            f"🚨 **NEW CUSTOMER INQUIRY & DEAL OPPORTUNITY!**\n"
            f"👤 **From:** {inquiry.customer_name} ({inquiry.customer_email})\n"
            f"📌 **Intent:** {intent} | **Priority:** {priority}\n"
            f"💰 **Deal Value:** ${inquiry.target_price:.2f} ➔ Closing Offer: **${discounted_price:.2f}** (-{inquiry.offered_discount_percent}%)\n"
            f"📝 **Summary:** Customer is asking about {inquiry.product_interest}. Pain points: {', '.join(pain_points)}.\n"
            f"🤝 **Deal Status:** Irresistible counter-offer generated and ready to close!"
        )

        summary_text = (
            f"Customer '{inquiry.customer_name}' inquired regarding '{inquiry.subject}'. "
            f"Detected intent as '{intent}' with deal closing opportunity at ${discounted_price:.2f}."
        )

        return DealAnalysisResult(
            summary=summary_text,
            customer_intent=intent,
            deal_priority=priority,
            estimated_deal_value=f"${discounted_price:.2f}",
            key_pain_points=pain_points,
            suggested_strategy=f"Offer instant {inquiry.offered_discount_percent}% discount and emphasize lifetime license.",
            closing_reply_subject=reply_subject,
            closing_reply_body=reply_body,
            instant_chat_alert=chat_alert,
            one_click_send_url=one_click_url
        )
