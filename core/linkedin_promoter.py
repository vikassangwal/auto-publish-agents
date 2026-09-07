"""
LinkedIn Promotion & Viral Post Generator.
Creates engagement-optimized social media posts with 1-Click Share links
to drive organic traffic and sales to newly published digital products.
"""
import urllib.parse
from typing import Dict, Any
from core.models import ProductMetadata

class LinkedInPromoter:
    @staticmethod
    def generate_promotion(product: ProductMetadata, primary_link: str) -> Dict[str, Any]:
        """
        Creates viral, high-converting LinkedIn post copy + 1-Click Share URL.
        """
        headline = f"🚀 Just launched: {product.title}!"
        tagline = product.tagline or "Supercharge your productivity with this automated system."
        
        feature_bullets = "\n".join([f"✅ {feat}" for feat in product.key_features[:4]])
        
        clean_tags = [
            f"#{t.replace(' ', '').replace('-', '')}"
            for t in product.tags[:5] if t
        ]
        if "#Productivity" not in clean_tags:
            clean_tags.append("#Productivity")
        if "#DigitalProducts" not in clean_tags:
            clean_tags.append("#DigitalProducts")
        
        tags_str = " ".join(clean_tags)
        
        post_copy = (
            f"{headline}\n\n"
            f"{tagline}\n\n"
            f"Key Highlights:\n"
            f"{feature_bullets}\n\n"
            f"Format: {product.format_category}\n"
            f"Price: ${product.price_usd:.2f} (Instant Download)\n\n"
            f"🔗 Access the template here: {primary_link}\n\n"
            f"💬 Let me know your thoughts in the comments below!\n\n"
            f"{tags_str}"
        )

        encoded_url = urllib.parse.quote(primary_link)
        one_click_share_url = f"https://www.linkedin.com/sharing/share-offsite/?url={encoded_url}"

        return {
            "headline": headline,
            "post_copy": post_copy,
            "one_click_share_url": one_click_share_url
        }
