from pathlib import Path
import json

PLATFORMS = [('Gumroad', 'high', 'Digital downloads and creator products', 'api_or_browser'), ('Payhip', 'high', 'Digital downloads', 'api_or_browser'), ('Sellfy', 'high', 'Digital products', 'api_or_browser'), ('Lemon Squeezy', 'high', 'Digital products/software', 'api'), ('Whop', 'high', 'Digital products and memberships', 'api_or_browser'), ('Etsy', 'medium', 'Digital templates/downloadables', 'browser_or_review'), ('Creative Market', 'medium', 'Design assets/templates', 'browser_or_review'), ('Product Hunt', 'medium', 'Product launch/discovery', 'launch_workflow'), ('BetaList', 'medium', 'Startup/product discovery', 'submission'), ('CodeCanyon', 'low', 'Code/software marketplace; not a natural fit for this XLSX', 'review'), ('Fiverr', 'low', 'Service marketplace; use only if sold as a service', 'review'), ('Upwork', 'low', 'Freelance service marketplace', 'review'), ('Amazon KDP', 'low', 'Books/eBooks; not a direct fit for this XLSX', 'review'), ('Podia', 'low', 'Courses/memberships/digital products', 'review'), ('Graphy', 'low', 'Education/course platform', 'review'), ('TagMango', 'low', 'Creator/education products', 'review')]

def analyze_product(path):
    return {
        "file": Path(path).name,
        "type": "Excel investment portfolio tracker",
        "positioning": "Investment portfolio-management workbook covering holdings, transactions, performance, allocation/risk, dividends, goals/SIP, rebalancing, scenarios, reports and investment journal.",
        "primary_channels": ["Gumroad", "Payhip", "Sellfy", "Lemon Squeezy", "Whop"],
        "secondary_channels": ["Etsy", "Creative Market"],
        "launch_channels": ["Product Hunt", "BetaList"],
    }

def route():
    return [{"platform": p, "fit": f, "reason": r, "publishing_mode": m}
            for p, f, r, m in PLATFORMS]

def listing_brief():
    return {
        "title": "Ultimate Investment Portfolio Tracker Pro",
        "category": "Personal Finance / Investment Tracking",
        "format": "Excel workbook",
        "benefits": ["Holdings and transaction tracking", "Portfolio performance review",
                    "Allocation and risk monitoring", "Dividend/income tracking",
                    "Goals and SIP planning", "Rebalancing drift review",
                    "Scenario analysis", "Investment journal and reports"]
    }

if __name__ == "__main__":
    out = {
        "product": analyze_product("Ultimate_Investment_Portfolio_Tracker_Pro.xlsx"),
        "platforms": route(),
        "listing_brief": listing_brief(),
        "email_monitoring": {
            "watch_for": ["verification", "approval", "rejection", "action required"],
            "human_approval": ["OTP", "CAPTCHA", "identity verification", "security challenges"]
        }
    }
    print(json.dumps(out, ensure_ascii=False, indent=2))
