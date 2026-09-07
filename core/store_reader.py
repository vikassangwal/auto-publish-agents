"""
Store Intelligence & Analytics Reader.
Enables ChatGPT Custom GPT and AI agents to query live sales, orders,
and product listings across Gumroad, Lemon Squeezy, Etsy, WooCommerce, and Shopify.
"""
import os
import json
import requests
from pathlib import Path
from typing import Dict, Any, List, Optional
from core.config import Config

class StoreReader:
    def __init__(self):
        self.config_path = Path(__file__).resolve().parent.parent / "websites.json"
        self.personal_sites = self._load_personal_sites()

    def _load_personal_sites(self) -> List[Dict[str, Any]]:
        try:
            from core.dynamic_store_registry import DynamicStoreRegistry
            return DynamicStoreRegistry().get_all_stores()
        except Exception:
            if not self.config_path.exists():
                return []
            try:
                return json.loads(self.config_path.read_text(encoding="utf-8"))
            except Exception:
                return []

    def get_store_connections(self) -> List[Dict[str, Any]]:
        """Returns connection and readiness status of all supported stores."""
        connections = []

        # 1. Marketplaces
        gumroad_key = Config.get("GUMROAD_ACCESS_TOKEN")
        connections.append({
            "platform": "Gumroad",
            "type": "Marketplace",
            "status": "API_ACTIVE" if gumroad_key and not gumroad_key.startswith("your_") else "BROWSER_DRAFT_READY",
            "mode": "Direct REST API" if gumroad_key and not gumroad_key.startswith("your_") else "1-Click Draft Automation",
            "can_read_sales": bool(gumroad_key and not gumroad_key.startswith("your_"))
        })

        lemon_key = Config.get("LEMON_SQUEEZY_API_KEY")
        connections.append({
            "platform": "Lemon Squeezy",
            "type": "Marketplace",
            "status": "API_ACTIVE" if lemon_key and not lemon_key.startswith("your_") else "BROWSER_DRAFT_READY",
            "mode": "Direct REST API" if lemon_key and not lemon_key.startswith("your_") else "1-Click Draft Automation",
            "can_read_sales": bool(lemon_key and not lemon_key.startswith("your_"))
        })

        etsy_key = Config.get("ETSY_API_KEY")
        connections.append({
            "platform": "Etsy",
            "type": "Marketplace",
            "status": "API_ACTIVE" if etsy_key and not etsy_key.startswith("your_") else "BROWSER_DRAFT_READY",
            "mode": "Listing Editor Integration",
            "can_read_sales": bool(etsy_key and not etsy_key.startswith("your_"))
        })

        for plat in ["Payhip", "Whop", "Stan Store", "Sellfy", "Cosmofeed", "Instamojo", "Razorpay Pages"]:
            connections.append({
                "platform": plat,
                "type": "Marketplace",
                "status": "BROWSER_DRAFT_READY",
                "mode": "1-Click Draft Publishing",
                "can_read_sales": False
            })

        # 2. Personal Websites from websites.json
        for site in self.personal_sites:
            p_type = site.get("type", "custom_webhook")
            auth = site.get("auth", {})
            has_auth = any(v and not str(v).startswith("your_") for v in auth.values())
            connections.append({
                "platform": site.get("name", "Personal Site"),
                "type": f"Personal ({p_type.capitalize()})",
                "status": "CONNECTED" if has_auth else "STANDBY (Needs Auth Token)",
                "mode": "Direct REST API Deploy",
                "url": site.get("url", ""),
                "can_read_sales": p_type in ["woocommerce", "shopify"] and has_auth
            })

        return connections

    def get_analytics(self) -> Dict[str, Any]:
        """Fetches sales and orders summary across connected platforms."""
        total_revenue_usd = 0.0
        total_orders = 0
        total_products_live = 0
        platform_stats = []

        # 1. Gumroad live reader
        gumroad_key = Config.get("GUMROAD_ACCESS_TOKEN")
        if gumroad_key and not gumroad_key.startswith("your_"):
            try:
                res = requests.get(
                    "https://api.gumroad.com/v2/sales",
                    headers={"Authorization": f"Bearer {gumroad_key}"},
                    timeout=5
                )
                if res.status_code == 200:
                    data = res.json()
                    sales = data.get("sales", [])
                    rev = sum(float(s.get("price", 0)) / 100.0 for s in sales)
                    total_revenue_usd += rev
                    total_orders += len(sales)
                    platform_stats.append({
                        "platform": "Gumroad",
                        "status": "ONLINE",
                        "orders_count": len(sales),
                        "revenue_usd": round(rev, 2),
                        "currency": "USD"
                    })
                else:
                    platform_stats.append({
                        "platform": "Gumroad",
                        "status": f"API_ERROR_{res.status_code}",
                        "orders_count": 0,
                        "revenue_usd": 0.0
                    })
            except Exception as e:
                platform_stats.append({
                    "platform": "Gumroad",
                    "status": "CONNECTION_TIMEOUT",
                    "orders_count": 0,
                    "revenue_usd": 0.0
                })
        else:
            platform_stats.append({
                "platform": "Gumroad",
                "status": "STANDBY (Draft Mode Active)",
                "orders_count": 0,
                "revenue_usd": 0.0,
                "note": "Add GUMROAD_ACCESS_TOKEN to view live revenue"
            })

        # 2. Lemon Squeezy live reader
        lemon_key = Config.get("LEMON_SQUEEZY_API_KEY")
        if lemon_key and not lemon_key.startswith("your_"):
            try:
                res = requests.get(
                    "https://api.lemonsqueezy.com/v1/orders",
                    headers={
                        "Accept": "application/vnd.api+json",
                        "Authorization": f"Bearer {lemon_key}"
                    },
                    timeout=5
                )
                if res.status_code == 200:
                    orders = res.json().get("data", [])
                    rev = sum(float(o.get("attributes", {}).get("total_usd", 0)) / 100.0 for o in orders)
                    total_revenue_usd += rev
                    total_orders += len(orders)
                    platform_stats.append({
                        "platform": "Lemon Squeezy",
                        "status": "ONLINE",
                        "orders_count": len(orders),
                        "revenue_usd": round(rev, 2),
                        "currency": "USD"
                    })
            except Exception:
                pass
        else:
            platform_stats.append({
                "platform": "Lemon Squeezy",
                "status": "STANDBY (Draft Mode Active)",
                "orders_count": 0,
                "revenue_usd": 0.0
            })

        # 3. Personal Websites (WooCommerce / Shopify)
        for site in self.personal_sites:
            s_name = site.get("name", "Site")
            s_type = site.get("type")
            auth = site.get("auth", {})
            if s_type == "woocommerce" and auth.get("consumer_key") and not auth["consumer_key"].startswith("your_"):
                try:
                    res = requests.get(
                        f"{site.get('url')}/wp-json/wc/v3/reports/sales",
                        auth=(auth["consumer_key"], auth.get("consumer_secret", "")),
                        timeout=5
                    )
                    if res.status_code == 200:
                        report_data = res.json()
                        total_sales = float(report_data[0].get("total_sales", 0.0)) if report_data else 0.0
                        total_revenue_usd += total_sales
                        platform_stats.append({
                            "platform": s_name,
                            "type": "WooCommerce",
                            "status": "ONLINE",
                            "revenue": round(total_sales, 2)
                        })
                except Exception:
                    pass
            else:
                platform_stats.append({
                    "platform": s_name,
                    "type": s_type,
                    "status": "READY_FOR_DEPLOY",
                    "revenue": 0.0
                })

        return {
            "summary": {
                "total_revenue_usd": round(total_revenue_usd, 2),
                "total_orders_count": total_orders,
                "total_connected_platforms": len(platform_stats),
                "status": "OPERATIONAL"
            },
            "platforms": platform_stats
        }

    def list_all_products(self) -> List[Dict[str, Any]]:
        """Retrieves list of products available, published, and drafted."""
        products = []

        # 1. Base Portfolio Tracker template
        products.append({
            "id": "prod_master_portfolio_tracker",
            "title": "Ultimate Investment Portfolio Tracker Pro",
            "format": "Macro-Free Excel (.xlsx) + Google Sheets",
            "price_usd": 29.0,
            "price_inr": 1999.0,
            "status": "READY_TO_DISTRIBUTE",
            "target_channels": ["Gumroad", "Etsy", "Lemon Squeezy", "WooCommerce", "Shopify", "Whop", "Payhip"]
        })

        # 2. Check Gumroad for live products
        gumroad_key = Config.get("GUMROAD_ACCESS_TOKEN")
        if gumroad_key and not gumroad_key.startswith("your_"):
            try:
                res = requests.get(
                    "https://api.gumroad.com/v2/products",
                    headers={"Authorization": f"Bearer {gumroad_key}"},
                    timeout=5
                )
                if res.status_code == 200:
                    for p in res.json().get("products", []):
                        products.append({
                            "id": p.get("id"),
                            "title": p.get("name"),
                            "format": "Digital Product",
                            "price_usd": float(p.get("price", 0)) / 100.0,
                            "platform": "Gumroad",
                            "status": "PUBLISHED",
                            "url": p.get("short_url") or p.get("url")
                        })
            except Exception:
                pass

        return products
