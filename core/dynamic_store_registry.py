"""
Dynamic Store & Website Registry.
Allows ChatGPT Custom GPT or AI agents to dynamically add, configure,
and register new websites (WooCommerce, Shopify, Webhooks, Marketplaces) on the fly.
"""
import os
import json
from pathlib import Path
from typing import Dict, Any, List, Optional

class DynamicStoreRegistry:
    def __init__(self):
        self.project_root = Path(__file__).resolve().parent.parent
        self.static_file = self.project_root / "websites.json"
        
        # Temp storage for serverless / Vercel runtime
        if os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME"):
            import tempfile
            self.dynamic_file = Path(tempfile.gettempdir()) / "custom_websites.json"
        else:
            self.dynamic_file = self.project_root / "storage" / "custom_websites.json"
            try:
                self.dynamic_file.parent.mkdir(parents=True, exist_ok=True)
            except Exception:
                pass

    def get_all_stores(self) -> List[Dict[str, Any]]:
        """Returns combined list of base websites and dynamically added stores."""
        stores = []
        seen_names = set()

        # 1. Base stores from websites.json
        if self.static_file.exists():
            try:
                base_data = json.loads(self.static_file.read_text(encoding="utf-8"))
                for s in base_data:
                    if s.get("enabled", True):
                        stores.append(s)
                        seen_names.add(s.get("name", "").lower())
            except Exception:
                pass

        # 2. Dynamic stores added via Custom GPT
        if self.dynamic_file.exists():
            try:
                dyn_data = json.loads(self.dynamic_file.read_text(encoding="utf-8"))
                for s in dyn_data:
                    if s.get("name", "").lower() not in seen_names:
                        stores.append(s)
                        seen_names.add(s.get("name", "").lower())
            except Exception:
                pass

        return stores

    def register_store(
        self,
        name: str,
        url: str,
        store_type: str = "woocommerce",
        api_key: Optional[str] = None,
        api_secret: Optional[str] = None,
        new_product_url: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Saves a new website or marketplace permanently so Custom GPT can deploy to it immediately.
        """
        clean_url = url.strip().rstrip("/")
        s_type = store_type.lower().strip()
        
        if s_type == "woocommerce":
            endpoint = f"{clean_url}/wp-json/wc/v3/products"
            creds = {"consumer_key": api_key or "", "consumer_secret": api_secret or ""}
        elif s_type == "shopify":
            endpoint = f"{clean_url}/admin/api/2023-10/products.json"
            creds = {"access_token": api_key or ""}
        else:
            endpoint = f"{clean_url}/api/products"
            creds = {"access_token": api_key or ""}

        new_store = {
            "id": f"site_{name.lower().replace(' ', '_')}",
            "name": name,
            "url": clean_url,
            "type": s_type,
            "api_endpoint": endpoint,
            "credentials": creds,
            "new_product_url": new_product_url or clean_url,
            "enabled": True,
            "added_via": "Custom GPT Action"
        }

        # Load existing dynamic stores
        existing = []
        if self.dynamic_file.exists():
            try:
                existing = json.loads(self.dynamic_file.read_text(encoding="utf-8"))
            except Exception:
                existing = []

        # Update or add
        filtered = [s for s in existing if s.get("name", "").lower() != name.lower()]
        filtered.append(new_store)

        try:
            self.dynamic_file.write_text(json.dumps(filtered, indent=2), encoding="utf-8")
        except Exception:
            pass

        # If on local writable disk, also update websites.json
        if not (os.getenv("VERCEL") or os.getenv("AWS_LAMBDA_FUNCTION_NAME")) and self.static_file.exists():
            try:
                static_list = json.loads(self.static_file.read_text(encoding="utf-8"))
                static_filtered = [s for s in static_list if s.get("name", "").lower() != name.lower()]
                static_filtered.append(new_store)
                self.static_file.write_text(json.dumps(static_filtered, indent=2), encoding="utf-8")
            except Exception:
                pass

        return new_store
